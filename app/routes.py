import os
import datetime
import json
import re
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from app.forms import AccountForm, CityForm, MessageForm, ScheduleForm, SettingsForm
import app.data_manager as dm

# Conditionally import automation-related modules
AUTOMATION_DISABLED = os.environ.get('DISABLE_AUTOMATION', 'false').lower() == 'true'

if not AUTOMATION_DISABLED:
    from app.tasks import start_bot_task
else:
    # Define a dummy function for the disabled bot
    def start_bot_task(account_id, city_id, message_id, max_posts=3, image_path=None, group_id=None):
        dm.add_log("Automation is disabled in this deployment. Use the local version for full features.", 
                  "warning", group_id=group_id)
        return {"success": False, "message": "Automation disabled in cloud deployment"}

bp = Blueprint('main', __name__)

# Utility class for pagination
class Pagination:
    """Simple pagination class similar to Flask-SQLAlchemy's Pagination"""
    
    def __init__(self, data):
        self.items = data['items']
        self.page = data['page']
        self.per_page = data['per_page']
        self.total = data['total']
        self.pages = data['pages']
        self.has_prev = self.page > 1
        self.has_next = self.page < self.pages
        self.prev_num = self.page - 1 if self.page > 1 else None
        self.next_num = self.page + 1 if self.page < self.pages else None
    
    def iter_pages(self):
        return range(1, self.pages + 1)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@bp.route('/')
def dashboard():
    """Dashboard page showing active accounts and controls"""
    accounts = dm.get_accounts()
    cities = dm.get_cities()
    messages = dm.get_messages()
    
    # Get recent logs (first page only)
    logs = dm.get_logs(page=1, per_page=5)
    
    # If automation is disabled, add a notification
    cloud_mode = AUTOMATION_DISABLED
    
    return render_template('dashboard.html', 
                          accounts=accounts,
                          cities=cities,
                          messages=messages,
                          logs=logs.get('items', []),
                          cloud_mode=cloud_mode)

@bp.route('/accounts', methods=['GET', 'POST'])
def accounts():
    form = AccountForm()
    if form.validate_on_submit():
        dm.add_account(
            email=form.email.data,
            password=form.password.data,
            active=form.active.data
        )
        flash('Account added successfully', 'success')
        return redirect(url_for('main.accounts'))
    
    accounts = dm.get_accounts()
    
    # Format datetime fields for display
    for account in accounts:
        if account.get('last_used'):
            account['last_used'] = datetime.datetime.fromisoformat(account['last_used'])
        else:
            account['last_used'] = None
        
        # Handle created_at date formatting
        if account.get('created_at'):
            account['created_at'] = datetime.datetime.fromisoformat(account['created_at'])
    
    return render_template('accounts.html', form=form, accounts=accounts)

@bp.route('/cities', methods=['GET', 'POST'])
def cities():
    form = CityForm()
    if form.validate_on_submit():
        dm.add_city(
            name=form.name.data,
            radius=form.radius.data
        )
        flash('City added successfully', 'success')
        return redirect(url_for('main.cities'))
    
    cities = dm.get_cities()
    
    # Format datetime fields for display
    for city in cities:
        if city.get('created_at'):
            city['created_at'] = datetime.datetime.fromisoformat(city['created_at'])
    
    return render_template('cities.html', form=form, cities=cities)

@bp.route('/messages', methods=['GET', 'POST'])
def messages():
    form = MessageForm()
    if form.validate_on_submit():
        image_filename = None
        
        # Handle image upload
        if form.image.data:
            image = form.image.data
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image_filename = filename
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        
        dm.add_message(
            content=form.content.data,
            image=image_filename
        )
        flash('Message added successfully', 'success')
        return redirect(url_for('main.messages'))
    
    messages = dm.get_messages()
    
    # Format datetime fields for display
    for message in messages:
        if message.get('created_at'):
            message['created_at'] = datetime.datetime.fromisoformat(message['created_at'])
    
    return render_template('messages.html', form=form, messages=messages)

@bp.route('/schedules', methods=['GET', 'POST'])
def schedules():
    form = ScheduleForm()
    if form.validate_on_submit():
        dm.add_schedule(
            start_time=form.start_time.data.strftime('%H:%M'),
            end_time=form.end_time.data.strftime('%H:%M'),
            active=form.active.data
        )
        flash('Schedule added successfully', 'success')
        return redirect(url_for('main.schedules'))
    
    schedules = dm.get_schedules()
    
    # Format datetime fields for display
    for schedule in schedules:
        if schedule.get('created_at'):
            schedule['created_at'] = datetime.datetime.fromisoformat(schedule['created_at'])
        if schedule.get('start_time'):
            parts = schedule['start_time'].split(':')
            schedule['start_time'] = datetime.time(int(parts[0]), int(parts[1]))
        if schedule.get('end_time'):
            parts = schedule['end_time'].split(':')
            schedule['end_time'] = datetime.time(int(parts[0]), int(parts[1]))
    
    return render_template('schedules.html', form=form, schedules=schedules)

@bp.route('/start', methods=['POST'])
def start_bot():
    """Start the bot with the selected account, city, and message"""
    account_id = request.form.get('account_id')
    city_id = request.form.get('city_id')
    message_id = request.form.get('message_id')
    max_posts = int(request.form.get('max_posts', 3))
    
    if not account_id or not city_id or not message_id:
        flash('Please select an account, city, and message template.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    account = dm.get_account(account_id)
    city = dm.get_city(city_id)
    message = dm.get_message(message_id)
    
    if not account or not city or not message:
        flash('Invalid selection. Please try again.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Check if automation is disabled
    if AUTOMATION_DISABLED:
        flash('Automation is disabled in this cloud deployment. Please use the local version for full features.', 'warning')
        dm.add_log(f"Attempted to start bot with account {account['email']} in {city['name']} but automation is disabled.",
                 "warning")
        return redirect(url_for('main.dashboard'))
    
    # Get the image path if an image file was uploaded
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename != '' and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = file_path
    
    # Add a log entry for starting the bot
    group_id = dm.generate_id()
    dm.add_log(f"Starting bot for account {account['email']} in {city['name']}", "info", group_id=group_id)
    
    # Start the bot in a background thread
    result = start_bot_task(account_id, city_id, message_id, max_posts, image_path, group_id)
    
    if result.get("success", False):
        flash('Bot started successfully! Check logs for details.', 'success')
    else:
        flash(f"Failed to start bot: {result.get('message', 'Unknown error')}", 'danger')
    
    return redirect(url_for('main.logs'))

@bp.route('/logs')
def logs():
    page = request.args.get('page', 1, type=int)
    group_id = request.args.get('group_id', None)
    
    # Default logs data structure if errors occur
    default_logs = {'items': [], 'page': 1, 'pages': 0, 'total': 0, 'per_page': 50}
    
    # If specific group_id is provided, show logs for that group only
    if group_id:
        try:
            logs_data = dm.get_logs(page=page, per_page=50, group_id=group_id)
            
            # Ensure logs_data has the proper structure
            if not isinstance(logs_data, dict) or 'items' not in logs_data:
                print(f"Invalid logs data structure for group {group_id}: {logs_data}")
                logs_data = default_logs
            elif not logs_data.get('items'):
                print(f"No logs found for group {group_id}")
            
            # Check if there are bot start messages to extract account info
            account_info = {}
            for log in logs_data.get('items', []):
                if "Starting bot for account" in log.get('message', ''):
                    try:
                        match = re.search(r"Starting bot for account: (\w+)", log.get('message', ''))
                        if match:
                            account_id = match.group(1)
                            account = dm.get_account_by_id(account_id)
                            if account:
                                account_info = account
                                break
                    except Exception as e:
                        print(f"Error extracting account info: {e}")
            
            return render_template('logs.html', logs=logs_data, group_id=group_id, 
                                  account_info=account_info, title='Bot Run Logs')
        except Exception as e:
            print(f"Error retrieving logs for group {group_id}: {str(e)}")
            flash(f"Error retrieving logs: {str(e)}", 'danger')
            return render_template('logs.html', logs=default_logs, group_id=group_id, title='Bot Run Logs')
    
    # Otherwise show general logs and find unique group_ids for bot runs
    try:
        logs_data = dm.get_logs(page=page, per_page=50)
        
        # Ensure logs_data has the proper structure 
        if not isinstance(logs_data, dict) or 'items' not in logs_data:
            print(f"Invalid logs data structure: {logs_data}")
            logs_data = default_logs
        elif not logs_data.get('items'):
            print("No logs found")
        
        # Find unique group_ids for bot runs (limited to last 10)
        bot_runs = []
        
        # Check if LOGS_FILE exists first
        if os.path.exists(dm.LOGS_FILE):
            try:
                with open(dm.LOGS_FILE, 'r') as f:
                    all_logs = json.load(f)
                    
                    # Extract unique group_ids with their timestamps
                    group_data = {}
                    for log in all_logs:
                        if log.get('group_id') and "Starting bot" in log.get('message', ''):
                            group_id = log.get('group_id')
                            if group_id not in group_data:
                                timestamp = log.get('timestamp', '')
                                account_match = re.search(r"Starting bot for account: (\w+)", log.get('message', ''))
                                account_id = account_match.group(1) if account_match else None
                                
                                group_data[group_id] = {
                                    'timestamp': timestamp,
                                    'account_id': account_id
                                }
                    
                    # Sort by timestamp (most recent first) and get top 10
                    sorted_groups = sorted(group_data.items(), 
                                          key=lambda x: x[1]['timestamp'] if x[1]['timestamp'] else '', 
                                          reverse=True)
                    
                    for group_id, data in sorted_groups[:10]:
                        account_name = None
                        if data.get('account_id'):
                            account = dm.get_account_by_id(data['account_id'])
                            if account:
                                account_name = account.get('username', 'Unknown')
                        
                        bot_runs.append({
                            'group_id': group_id,
                            'timestamp': data['timestamp'],
                            'account_name': account_name
                        })
            except Exception as e:
                print(f"Error loading bot runs: {e}")
                
        # Double check logs_data is correct before passing to template
        if logs_data is None or not isinstance(logs_data, dict) or 'items' not in logs_data:
            print("Logs data is None or invalid after processing")
            logs_data = default_logs
        
        print(f"Rendering logs.html with {len(logs_data.get('items', []))} logs for page {logs_data.get('page', 1)}")
        return render_template('logs.html', logs=Pagination(logs_data), bot_runs=bot_runs, title='System Logs')
    except Exception as e:
        print(f"Error retrieving logs: {str(e)}")
        flash(f"Error retrieving logs: {str(e)}", 'danger')
        return render_template('logs.html', logs=Pagination(default_logs), title='System Logs')

@bp.route('/settings', methods=['GET', 'POST'])
def settings():
    current_settings = dm.get_settings()
    form = SettingsForm()
    
    if request.method == 'GET':
        # Populate form with current settings
        form.run_interval.data = current_settings.get('run_interval', 30)
        form.max_posts_per_day.data = current_settings.get('max_posts_per_day', 10)
        form.timeout_between_actions.data = current_settings.get('timeout_between_actions', 5)
        form.enable_random_delays.data = current_settings.get('enable_random_delays', True)
    
    if form.validate_on_submit():
        # Update settings
        updated_settings = {
            'run_interval': form.run_interval.data,
            'max_posts_per_day': form.max_posts_per_day.data,
            'timeout_between_actions': form.timeout_between_actions.data,
            'enable_random_delays': form.enable_random_delays.data
        }
        dm.update_settings(updated_settings)
        flash('Settings updated successfully', 'success')
        return redirect(url_for('main.settings'))
    
    return render_template('settings.html', form=form)

@bp.route('/account/delete/<account_id>', methods=['POST'])
def delete_account(account_id):
    dm.delete_account(account_id)
    flash('Account deleted successfully', 'success')
    return redirect(url_for('main.accounts'))

@bp.route('/city/delete/<city_id>', methods=['POST'])
def delete_city(city_id):
    dm.delete_city(city_id)
    flash('City deleted successfully', 'success')
    return redirect(url_for('main.cities'))

@bp.route('/message/delete/<message_id>', methods=['POST'])
def delete_message(message_id):
    image_filename = dm.delete_message(message_id)
    
    # Delete the associated image file if it exists
    if image_filename:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    flash('Message deleted successfully', 'success')
    return redirect(url_for('main.messages'))

@bp.route('/schedule/delete/<schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):
    dm.delete_schedule(schedule_id)
    flash('Schedule deleted successfully', 'success')
    return redirect(url_for('main.schedules'))

@bp.route('/screenshots')
def screenshots():
    # Get all PNG files from the screenshots directory
    screenshots_dir = os.path.join(current_app.root_path, '..', 'screenshots')
    os.makedirs(screenshots_dir, exist_ok=True)  # Ensure directory exists
    
    screenshots = []
    
    if os.path.exists(screenshots_dir):
        # Get all PNG files with creation time
        for filename in os.listdir(screenshots_dir):
            if filename.lower().endswith('.png'):
                filepath = os.path.join('/screenshot', filename)
                created_at = datetime.datetime.fromtimestamp(
                    os.path.getctime(os.path.join(screenshots_dir, filename))
                )
                
                # Try to extract a descriptive name
                name_parts = filename.split('_')
                if len(name_parts) > 0:
                    description = name_parts[0].replace('_', ' ').title()
                else:
                    description = "Screenshot"
                    
                screenshots.append({
                    'filename': filename,
                    'filepath': filepath,
                    'created_at': created_at,
                    'description': description
                })
        
        # Sort screenshots by creation time (newest first)
        screenshots.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('screenshots.html', screenshots=screenshots)

@bp.route('/screenshot/<filename>')
def get_screenshot(filename):
    screenshots_dir = os.path.join(current_app.root_path, '..', 'screenshots')
    return send_from_directory(screenshots_dir, filename)

# Add a new route for Cloud Run status
@bp.route('/api/status')
def api_status():
    """API endpoint for checking system status"""
    status = {
        "app": "running",
        "timestamp": datetime.datetime.now().isoformat(),
        "automation_enabled": not AUTOMATION_DISABLED
    }
    return jsonify(status) 