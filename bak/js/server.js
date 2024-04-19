// server.js
const express = require('express');
const multer = require('multer');
const cors = require('cors'); // Import cors module
const fs = require('fs');
const dir = './uploads';
const ffmpeg = require('fluent-ffmpeg');
const ffmpegStatic = require('ffmpeg-static');

if (!fs.existsSync(dir)){
    fs.mkdirSync(dir, { recursive: true });
}



const app = express();
app.use(cors()); // Enable CORS for all routes
const port = 3003;

// set up storage to store the audio file
const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        cb(null, 'uploads/')
    },
    filename: function(req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9)
        cb(null, file.fieldname + '-' + uniqueSuffix + '.wav') // Customize file name
    }
});

//const upload = multer({ storage: storage });
// const storage = multer.memoryStorage(); // Using memory storage
const upload = multer({ storage: storage });    // Using memory storage
// const upload = multer({ dest: 'uploads/' });
app.post('/upload', upload.single('audio'), (req, res) => {
    console.log(req.file); // This is where you'd process the audio, then generate and send a response.
    // if no audio file is sent, send a 400 status code
    if (!req.file) {
        return res.status(400).send('No files were uploaded.');
    }
    // convert the audio received to a wav and save it
    ffmpeg(req.file.buffer)
        .setFfmpegPath(ffmpegStatic)
        .toFormat('wav')
        .on('stderr', function(stderrLine) {
        console.log(stderrLine);
    })
        .on('error', function(err, stdout, stderr) {
        console.log('Error: ' + err.message);
        console.log('ffmpeg stdout:\n' + stdout);
        console.log('ffmpeg stderr:\n' + stderr);
    })
        .on('end', () => {
            console.log('file has been converted successfully');
        }).save(`uploads/${req.file.filename}`);
        // .save(`uploads/${req.file.filename}`);



    // For simplicity, let's just send back a static file as a response. In a real scenario, you'd process the audio and generate a response dynamically.
    res.sendFile(__dirname + '/response/welcome.wav');
});

app.listen(port, () => console.log(`Listening on port ${port}`));
