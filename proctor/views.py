from flask import flash, redirect, render_template, url_for, request, Response
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash
from .camera import VideoCamera
import os
from . import app, lm
from .models import Note, User, Enrollment
from .forms import LoginForm, SignupForm, AddNoteForm, EnrollmentForm, AdminForm


from werkzeug.utils import secure_filename

from flask_table import Table, Col
class Results(Table):
    id = Col('Id', show=False)
    artist = Col('Artist')
    title = Col('Title')
    release_date = Col('Release Date')
    publisher = Col('Publisher')
    media_type = Col('Media')

@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

ALLOWED_EXTENSIONS = set([ 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = "user_info"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signup', methods=['POST','GET'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        new = User(username=form.username.data, email=form.email.data, password=form.password.data)
        new.save()
        parent_dir=os.getcwd()
        path = os.path.join(parent_dir, 'user_info')
        dirpath = os.path.join(path, form.username.data)
        os.mkdir(dirpath)
        flash("Registration was successful")
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)
@app.route('/admin', methods=['POST','GET'])
def admin():
    
    return render_template('confirm.html')

@app.route('/verification', methods=['POST','GET'])
def verification():
    return render_template('verification.html')
    


@app.route('/login', methods=['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash("login successful")
            return redirect(url_for('home'))
        flash("Incorrect password or email")
    return render_template('login.html', form=form)

@app.route('/enrollment', methods=['POST','GET'])
def enrollment():
    form = EnrollmentForm()
    if form.validate_on_submit():
        new = Enrollment(username=form.username.data, email=form.email.data, exam=form.exam.data)
        new.save()
        
        flash("Enrollment was successful")
        return redirect(url_for('login'))
    return render_template('enrollment.html', form=form)

@app.route('/examiner', methods=['POST','GET'])
def examiner():
    '''form = AdminForm()
   if form.validate_on_submit():
        #new = Enrollment(username=form.username.data, email=form.email.data, exam=form.exam.data)
        #new.save()
        
        flash("Enrollment was successful")
        return redirect(url_for('login'))'''
    return render_template('admin.html')
@login_required
@app.route('/upload_file', methods=['POST','GET'])   
def upload_file():
    user_name=current_user.username
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect("verification.html")
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect("verification.html")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = user_name+"proof.jpg"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],user_name, filename))
            flash('File successfully uploaded')
            return redirect('/')
        else:
            flash('Allowed file types are txt, pdf, png, jpg, jpeg, gif')
            return redirect("verification.html", filename=app.config['UPLOAD_FOLDER']+ filename)
@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename=app.config['UPLOAD_FOLDER']+ filename), code=301)

@login_required
@app.route('/capture', methods=['POST','GET'])   
def capture():
    import cv2
    user_name=current_user.username
    
    filename= os.path.join(app.config['UPLOAD_FOLDER'],user_name,user_name+".jpg")

    videoCaptureObject = cv2.VideoCapture(0)
    result = True
    while(result):
        ret,frame = videoCaptureObject.read()
        cv2.imwrite(filename,frame)
        flash('File successfully uploaded')
        result = False
    videoCaptureObject.release()
    cv2.destroyAllWindows()
    
    return redirect(url_for('verification'))
    

@app.route('/results', methods=['POST','GET'])
def results(search):
    return render_template('results.html')
    '''results = []
    search_string = search.data['search']
    if search.data['search'] == '':
        qry = db_session.query(Album)
        results = qry.all()
    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        table = Results(results)
        table.border = True
        return render_template('results.html', table=table)'''




@login_required
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@login_required
@app.route('/home')
def home():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', notes=notes)

@login_required
@app.route('/add', methods=['POST','GET'])
def add():
    form = AddNoteForm()
    notes = Note.query.filter_by(user_id=current_user.id).all()
    if form.validate_on_submit():
        new = Note(title=form.title.data, content=form.content.data, user_id=current_user.id)
        new.save()
        flash("Note created successfully!")
        return redirect(url_for('home'))
    return render_template('new.html', form=form, notes=notes)

@login_required
@app.route('/view/<id>')
def view(id):
    note = Note.query.get(id)
    notes = Note.query.filter_by(user_id=current_user.id).all()
    return render_template('note.html', note=note, notes=notes)

