from flask import request, Flask
from subprocess import Popen, PIPE, STDOUT
import yaml
from werkzeug.utils import secure_filename
import time

app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['txt', 'pdf'])

with open('/home/longnhit/workspace/moses-restful/config.yaml', 'r') as f:
    doc = yaml.load(f)
    runCommand = doc['sample-models']['command']
    homeDir = doc['sample-models']['homeDir']
    p = Popen([runCommand], cwd=homeDir, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def translate(text):
    start_time = time.time()
    """
    Run translation model using config
    """
    with open('/home/longnhit/workspace/moses-restful/config.yaml', 'r') as f:
        doc = yaml.load(f)
    fileIn = doc['sample-models']['in']
    fileOut = doc['sample-models']['out']
    homeDir = doc['sample-models']['homeDir']
    runCommand = doc['sample-models']['command']
    status = 'Files successfully read'
    # subprocess.call(['rm {} && rm {}'.format(fileIn, fileOut)], shell=True)
    text8 = text.encode('utf8')
    inputFile = open(fileIn, 'w')
    inputFile.write(text8.decode('utf8') + '\n')
    inputFile.close()
    # subprocess.call([runCommand], cwd=homeDir, shell=True)
    # readTranslate = open(fileOut, 'r')
    # translatedText = readTranslate.read()
    translated_text = p.communicate(text)[0].rstrip()
    # readTranslate.close()
    return {
            "STATUS": status,
            "LAN": 'N/A',
            "MODEL": str(homeDir),
            "CMD": str(runCommand),
            "URL": request.host_url.rstrip('/').encode('utf8'),
            "INPUT": text.encode('utf8'),
            "INPUT_SIZE": len(text.encode('utf8')),
            "INPUT_PATH": str(fileIn),            
            "OUTPUT": translated_text,
            "OUTPUT_SIZE": len(translated_text),
            "OUTPUT_PATH": str(fileOut),
            "DURATION": '%.3f seconds' % (time.time() - start_time)
    }


@app.route("/", methods=['GET'])
def instructions():
    return 'The Moses API is working! Try a GET request with text.\n'


@app.route("/<text>", methods=['GET'])
def user_get(text):
    """
    Translate text
    """
    text = translate(text)
    return text


@app.route("/upload", methods=['POST', 'PUT'])
def upload():
    """
    Tranlsate file
    """
    file = request.files['name']
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        text = file.read()
        text = translate(text)
        return text
    else:
        return ('Error reading file...\n')
