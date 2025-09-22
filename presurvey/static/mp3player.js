document.addEventListener("DOMContentLoaded", function () {
  const audioEl = document.getElementById('audioElement');
  const playPauseBtn = document.getElementById('playPauseBtn');
  const stopBtn = document.getElementById('stopBtn');
  const volUp = document.getElementById('volUp');
  const volDown = document.getElementById('volDown');
  const volumeVal = document.getElementById('volumeVal');
  const timeDisplay = document.getElementById('timeDisplay');
  const stateDisplay = document.getElementById('stateDisplay');

  if (!MP3_URL) {
    stateDisplay.textContent = 'State: No mp3_url provided.';
    return;
  }

  const wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: '#cfe7ff',
    progressColor: '#2b6cb0',
    cursorColor: '#1064a6',
    height: 90,
    normalize: true,
    responsive: true,
    backend: 'MediaElement'
  });

  wavesurfer.load(MP3_URL, audioEl);

  audioEl.addEventListener('timeupdate', updateTime);
  audioEl.addEventListener('loadedmetadata', updateTime);
  audioEl.addEventListener('play', () => updateState('Playing'));
  audioEl.addEventListener('pause', () => updateState('Paused'));
  audioEl.addEventListener('ended', () => {
    updateState('Ended');
    playPauseBtn.textContent = 'Play ▶';
    playPauseBtn.setAttribute('aria-pressed', 'false');
  });

  playPauseBtn.addEventListener('click', () => {
    if (audioEl.paused) {
      audioEl.play();
      playPauseBtn.textContent = 'Pause ⏸';
      playPauseBtn.setAttribute('aria-pressed', 'true');
    } else {
      audioEl.pause();
      playPauseBtn.textContent = 'Play ▶';
      playPauseBtn.setAttribute('aria-pressed', 'false');
    }
  });

  stopBtn.addEventListener('click', () => {
    audioEl.pause();
    audioEl.currentTime = 0;
    wavesurfer.seekTo(0);
    playPauseBtn.textContent = 'Play ▶';
    playPauseBtn.setAttribute('aria-pressed', 'false');
    updateState('Stopped');
    updateTime();
  });

  function setVolume(v) {
    v = Math.max(0, Math.min(1, v));
    wavesurfer.setVolume(v);
    audioEl.volume = v;
    volumeVal.textContent = Math.round(v * 100) + '%';
  }

  volUp.addEventListener('click', () => setVolume(audioEl.volume + 0.1));
  volDown.addEventListener('click', () => setVolume(audioEl.volume - 0.1));

  setVolume(1.0);

  wavesurfer.on('seek', progress => {
    const dur = audioEl.duration || 1;
    audioEl.currentTime = progress * dur;
  });

  function formatTime(s) {
    s = Math.floor(s);
    const m = String(Math.floor(s / 60)).padStart(2, '0');
    const sec = String(s % 60).padStart(2, '0');
    return `${m}:${sec}`;
  }

  function updateTime() {
    const cur = audioEl.currentTime || 0;
    const dur = audioEl.duration || 0;
    timeDisplay.textContent = `${formatTime(cur)} / ${formatTime(dur)}`;
  }

  function updateState(txt) {
    stateDisplay.textContent = 'State: ' + txt;
  }
});
