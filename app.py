from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Stamp, Coupon, EventConfig
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret-compliment-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize Database and default admin
with app.app_context():
    db.create_all()
    # Create default admin if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            name='최고 관리자',
            is_admin=True
        )
        db.session.add(admin)
        
        # Create default event config
        event = EventConfig(stamps_required_for_coupon=10, is_active=True)
        db.session.add(event)
        
        db.session.commit()

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('user_dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('로그인 정보가 올바르지 않습니다.', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('이미 존재하는 아이디입니다.', 'error')
            return redirect(url_for('register'))
            
        new_user = User(
            username=username,
            name=name,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        
        flash('회원가입이 완료되었습니다! 로그인해주세요.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))
        
    stamps = Stamp.query.filter_by(user_id=current_user.id).all()
    coupons = Coupon.query.filter_by(user_id=current_user.id).all()
    event_config = EventConfig.query.first()
    required = event_config.stamps_required_for_coupon if event_config else 10
    
    return render_template('user_dashboard.html', stamps=stamps, coupons=coupons, required=required)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
        
    users = User.query.filter_by(is_admin=False).all()
    event_config = EventConfig.query.first()
    
    # Calculate stats for each user (stamps count, coupons count)
    user_stats = []
    for u in users:
        stamps_count = Stamp.query.filter_by(user_id=u.id).count()
        coupons_count = Coupon.query.filter_by(user_id=u.id).count()
        user_stats.append({
            'user': u,
            'stamps': stamps_count,
            'coupons': coupons_count
        })
        
    recent_used_coupons = Coupon.query.filter_by(is_used=True).order_by(Coupon.used_at.desc()).limit(10).all()
        
    return render_template('admin_dashboard.html', user_stats=user_stats, event_config=event_config, recent_used_coupons=recent_used_coupons)

@app.route('/admin/user/<int:user_id>')
@login_required
def admin_user_detail(user_id):
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
        
    target_user = User.query.get_or_404(user_id)
    stamps = Stamp.query.filter_by(user_id=user_id).order_by(Stamp.granted_at.desc()).all()
    coupons = Coupon.query.filter_by(user_id=user_id).order_by(Coupon.granted_at.desc()).all()
    
    return render_template('admin_user_detail.html', target_user=target_user, stamps=stamps, coupons=coupons)

@app.route('/delete_stamp/<int:stamp_id>', methods=['POST'])
@login_required
def delete_stamp(stamp_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    stamp = Stamp.query.get_or_404(stamp_id)
    target_user_id = stamp.user_id
    db.session.delete(stamp)
    db.session.commit()
    flash('스탬프가 삭제되었습니다.', 'success')
    return redirect(url_for('admin_user_detail', user_id=target_user_id))

@app.route('/delete_coupon/<int:coupon_id>', methods=['POST'])
@login_required
def delete_coupon(coupon_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    coupon = Coupon.query.get_or_404(coupon_id)
    target_user_id = coupon.user_id
    db.session.delete(coupon)
    db.session.commit()
    flash('쿠폰이 삭제되었습니다.', 'success')
    return redirect(url_for('admin_user_detail', user_id=target_user_id))

@app.route('/use_coupon/<int:coupon_id>', methods=['POST'])
@login_required
def use_coupon(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    if coupon.user_id != current_user.id:
        flash('자신의 쿠폰만 사용할 수 있습니다.', 'error')
        return redirect(url_for('user_dashboard'))
        
    if coupon.is_used:
        flash('이미 사용된 쿠폰입니다.', 'error')
        return redirect(url_for('user_dashboard'))
        
    coupon.is_used = True
    coupon.used_at = datetime.utcnow()
    db.session.commit()
    flash('쿠폰을 성공적으로 사용했습니다!', 'success')
    return redirect(url_for('user_dashboard'))

@app.route('/grant_stamp/<int:user_id>', methods=['POST'])
@login_required
def grant_stamp(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    message = request.form.get('message', '참 잘했어요!')
    target_user = User.query.get(user_id)
    
    if target_user:
        new_stamp = Stamp(user_id=user_id, granted_by=current_user.id, message=message)
        db.session.add(new_stamp)
        db.session.commit()
        
        # Check auto coupon
        event_config = EventConfig.query.first()
        if event_config and event_config.is_active:
            stamps_count = Stamp.query.filter_by(user_id=user_id).count()
            if stamps_count > 0 and stamps_count % event_config.stamps_required_for_coupon == 0:
                auto_coupon = Coupon(user_id=user_id, reason=f'도장 {event_config.stamps_required_for_coupon}개 달성 보상!')
                db.session.add(auto_coupon)
                db.session.commit()
                flash(f'{target_user.name}님에게 도장 1개가 부여되었고, {event_config.stamps_required_for_coupon}개 달성으로 쿠폰도 자동 발급되었습니다!', 'success')
                return redirect(url_for('admin_dashboard'))
                
        flash(f'{target_user.name}님에게 도장 1개가 부여되었습니다!', 'success')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/grant_coupon/<int:user_id>', methods=['POST'])
@login_required
def grant_coupon(user_id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    reason = request.form.get('reason', '관리자 특별 부여 쿠폰')
    target_user = User.query.get(user_id)
    
    if target_user:
        new_coupon = Coupon(user_id=user_id, granted_by=current_user.id, reason=reason)
        db.session.add(new_coupon)
        db.session.commit()
        flash(f'{target_user.name}님에게 특별 쿠폰이 발급되었습니다!', 'success')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/update_event', methods=['POST'])
@login_required
def update_event():
    if not current_user.is_admin:
        return redirect(url_for('index'))
        
    required_stamps = request.form.get('required_stamps', type=int)
    if required_stamps and required_stamps > 0:
        event_config = EventConfig.query.first()
        if event_config:
            event_config.stamps_required_for_coupon = required_stamps
            db.session.commit()
            flash('이벤트 설정이 업데이트되었습니다.', 'success')
            
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
