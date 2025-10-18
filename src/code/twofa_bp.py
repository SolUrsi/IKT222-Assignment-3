from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_user, current_user
import pyotp
import qrcode
from io import BytesIO
import base64

from .models import db, User

twofa_bp = Blueprint('twofa', __name__, url_prefix='/2fa')

# Generate QR code data URL for 2FA setup
def get_qrcode_data_url(secret_key, username, app_name="SupurrSecretChatroom"): # Hard coded app name, could be made configurable but this is fine for a test project
    provisioning_uri = pyotp.totp.TOTP(secret_key).provisioning_uri(
        name=username,
        issuer_name=app_name
        )
    img = qrcode.make(provisioning_uri)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    # Encode the image to base64 for embedding in HTML
    return "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()

@twofa_bp.route("/2fa/mandatory-setup")
def setup_2fa_mandatory():
    # Retrieve the user ID that was set in the successful login 
    user_id = session.get('setup_2fa_user_id')
    
    if user_id:
        user = User.query.get(user_id)
        
        # Check if the user exists and still needs 2FA setup
        if user and not user.is_2fa_enabled:
            return redirect(url_for('twofa.setup_2fa'))
            
    # If they tried to skip, the session is gone, or they are already set up/logged in.
    flash("[SYSTEM] Access Denied. Log in to complete security setup.", "error")
    return redirect(url_for('auth.login'))


# 2FA Setup Route
@twofa_bp.route("/2fa/setup", methods=["GET", "POST"])
def setup_2fa():
    # Determine if the user is authenticated (A) or mandatory setup (B)

    # A. Case: User is ALREADY logged in (e.g., enabling 2FA from profile)
    if current_user.is_authenticated:
        user = current_user
        # If 2FA is already enabled, redirect away
        if user.is_2fa_enabled:
            flash("[SYSTEM] 2FA is already enabled.", "info")
            return redirect(url_for('main.room'))
            
    # B. Case: User is NOT logged in but is forced into mandatory setup
    else:
        user_id = session.get('setup_2fa_user_id')
        if not user_id:
            # They tried to access setup without credentials
            flash("[SYSTEM] Unauthorized setup attempt.", "error")
            return redirect(url_for('auth.login'))
        
        user = User.query.get(user_id)
        if not user or user.is_2fa_enabled:
            # User doesn't exist or is already set up
            session.pop('setup_2fa_user_id', None)
            flash("[SYSTEM] Invalid setup state.", "error")
            return redirect(url_for('auth.login'))

    if request.method == "GET":
        if '2fa_temp_secret' not in session:
            session['2fa_temp_secret'] = pyotp.random_base32()

        qr_data_url = get_qrcode_data_url(session['2fa_temp_secret'], user.username) 
        
        return render_template("2fa_setup.html", qr_data_url=qr_data_url)

    elif request.method == "POST":
        token = request.form.get("token")
        temp_secret = session.get('2fa_temp_secret')

        if not token or not temp_secret:
            flash("[SYSTEM] Setup error. Start again.", "error")
            session.pop('2fa_temp_secret', None)
            return redirect(url_for('main.room'))

        # Verify the entered code
        totp = pyotp.TOTP(temp_secret)
        if totp.verify(token):
            # Successful verification: Commit the secret to the user model
            user.otp_secret = temp_secret
            user.is_2fa_enabled = True
            db.session.commit()
            
            # If they were forced into setup (B), log them in now.
            if 'setup_2fa_user_id' in session:
                login_user(user)
                session.pop('setup_2fa_user_id', None) # Clean up the mandatory session key
                flash("[SYSTEM] 2FA enabled and agent active.", "success")
            else:
                # If they were already logged in (A), just confirm the setup.
                flash("[SYSTEM] 2FA enabled for agent.", "success")

            # Cleanup temporary secret
            session.pop('2fa_temp_secret', None)
            
            return redirect(url_for('main.room'))
        else:
            flash("[SYSTEM] Invalid code. Try again or rescan QR code.", "error")
            return redirect(url_for('twofa.setup_2fa'))

# 2FA Verification Route
@twofa_bp.route("/verify-2fa", methods=["GET", "POST"])
def verify_2fa():
    # Check if the user ID is in the session (meaning password was verified)
    user_id = session.get('2fa_user_id')
    
    if not user_id:
        flash("[SYSTEM] Access token required.", "error")
        return redirect(url_for('auth.login'))

    user = User.query.get(user_id)
    # Ensure the user exists and 2FA is enabled for them
    if not user or not user.is_2fa_enabled:
        session.pop('2fa_user_id', None)
        flash("[SYSTEM] Security conflict detected.", "error")
        return redirect(url_for('auth.login'))
        
    if request.method == "POST":
        token = request.form.get("token")
        
        # Use stored secret key to create the TOTP object
        totp = pyotp.TOTP(user.otp_secret)
        
        # Verify the token (valid_window=1 checks the current and previous 30-sec window)
        if totp.verify(token, valid_window=1):
            
            # Success: Log the user in and clean up the session
            login_user(user)
            session.pop('2fa_user_id', None)
            flash("[SYSTEM] 2FA verified. Agent now active.", "success")
            return redirect(url_for("main.room"))
        else:
            # Failure: Stay on the verification page
            flash("[SYSTEM] Invalid 2FA token. Access denied.", "error")
            return render_template("2fa_verify.html")

    # GET request: Display the verification form
    return render_template("2fa_verify.html")