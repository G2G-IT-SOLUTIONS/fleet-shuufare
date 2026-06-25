# Quick share options for running this repo locally

Options to expose your local server from your PC so others can test:

- Ngrok (recommended for quick demos):
  - Install: https://ngrok.com/download
  - (Optional) Authenticate: `ngrok authtoken <your-token>`
  - Run server and tunnel:
    ```powershell
    # from repo root
    pip install -r requirements.txt
    .\.venv\Scripts\Activate.ps1   # or activate your venv
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    # in another terminal
    ngrok http 8000
    ```
  - Share the `https://...ngrok.io` URL shown by ngrok.

- Cloudflare Tunnel (cloudflared):
  - Install: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation
  - Run:
    ```powershell
    # start your app first (uvicorn as above)
    cloudflared tunnel --url http://localhost:8000
    ```

- LocalTunnel (no install, ephemeral):
  ```powershell
  npx localtunnel --port 8000 --subdomain mydemo123
  ```

Notes & troubleshooting:
- Ensure the app binds to 0.0.0.0 (the uvicorn `--host 0.0.0.0` flag) so tunnels can reach it.
- Allow port 8000 through Windows Firewall if needed.
- If you want a stable publicly reachable URL, consider deploying to Render/Railway/Fly instead.

Helper script:
- There's a convenience script at `scripts/share_ngrok.ps1` that starts the app (using `.venv` if present) and launches ngrok if available.
