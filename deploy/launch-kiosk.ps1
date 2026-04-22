# Launch Kiosk in Chrome Fullscreen
Start-Process "chrome.exe" -ArgumentList @(
    "--kiosk",
    "--app=https://evotingdz.live/kiosk",
    "--disable-pinch",
    "--overscroll-history-navigation=0"
)
