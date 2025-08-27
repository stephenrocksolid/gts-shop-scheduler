# GTS-Scheduler Installation Guide for Offline Windows 10 Pro Server

This guide provides step-by-step instructions for installing the GTS-Scheduler application on an offline Windows 10 Pro server using Waitress, Nginx, and NSSM.

## Prerequisites

1. Windows 10 Pro Server
2. Python 3.8 or higher installed
3. Required software packages (download these on a machine with internet access):
   - Waitress
   - Nginx for Windows
   - NSSM (Non-Sucking Service Manager)
   - All Python dependencies (requirements.txt)

## Step 1: Prepare the Installation Files

1. On a machine with internet access:
   - Download all required Python packages using:
     ```bash
     pip download -r requirements.txt -d ./packages
     ```
   - Download Nginx for Windows from: http://nginx.org/en/download.html
   - Download NSSM from: https://nssm.cc/download
   - Download Waitress using:
     ```bash
     pip download waitress -d ./packages
     ```

2. Transfer all downloaded files to the offline server:
   - Copy the entire project directory
   - Copy the downloaded packages directory
   - Copy Nginx and NSSM installation files

## Step 2: Install Python Dependencies

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install the downloaded packages:
   ```bash
   pip install --no-index --find-links ./packages -r requirements.txt
   pip install --no-index --find-links ./packages waitress
   ```

## Step 3: Configure the Application

1. Create a `.env` file in the project root:
   ```
   DEBUG=False
   SECRET_KEY=your-secret-key-here
   ALLOWED_HOSTS=192.168.1.44,localhost,127.0.0.1
   ```

2. Run migrations:
   ```bash
   python manage.py migrate
   ```

3. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Step 4: Install and Configure Nginx

1. Extract the Nginx archive to `C:\nginx`

2. Create Nginx configuration file at `C:\nginx\conf\nginx.conf`:
   ```nginx
   worker_processes  1;

   events {
       worker_connections  1024;
   }

   http {
       include       mime.types;
       default_type  application/octet-stream;
       sendfile        on;
       keepalive_timeout  65;

       server {
           listen       80;
           server_name  192.168.1.44 localhost;

           location / {
               proxy_pass http://127.0.0.1:8000;
               proxy_set_header Host $host;
               proxy_set_header X-Real-IP $remote_addr;
               proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
               proxy_set_header X-Forwarded-Proto $scheme;
           }

           location /static/ {
               alias C:/path/to/your/project/static/;
           }

           location /media/ {
               alias C:/path/to/your/project/media/;
           }
       }
   }
   ```

3. Start Nginx:
   ```bash
   C:\nginx\nginx.exe
   ```

## Step 5: Configure Waitress with NSSM

1. Create a batch file `start_server.bat`:
   ```batch
   @echo off
   cd /d C:\path\to\your\project
   call venv\Scripts\activate
   waitress-serve --port=8000 gts_scheduler.wsgi:application
   ```

2. Install the service using NSSM:
   ```bash
   nssm install GTS-Scheduler "C:\path\to\your\project\start_server.bat"
   nssm set GTS-Scheduler AppDirectory "C:\path\to\your\project"
   nssm set GTS-Scheduler DisplayName "GTS Scheduler Service"
   nssm set GTS-Scheduler Description "GTS Scheduler Application Service"
   ```

3. Start the service:
   ```bash
   nssm start GTS-Scheduler
   ```

## Step 6: Verify Installation

1. Open a web browser and navigate to `http://localhost` or your server's IP address
2. The application should be accessible
3. Try logging in with the superuser credentials created earlier

## Network Access

### Accessing from Local Network

1. On the server machine (192.168.1.44):
   - Ensure Windows Firewall allows incoming connections on port 80
   - Open Windows Defender Firewall with Advanced Security
   - Add a new inbound rule for port 80 (TCP)
   - Allow the connection for your local network profile

2. From any machine in your local network:
   - Open a web browser
   - Navigate to `http://192.168.1.44`
   - The application should be accessible

### Troubleshooting Network Access

1. If you cannot access the application:
   - Verify the server's IP address is correct
   - Check if Windows Firewall is blocking the connection
   - Ensure both Nginx and the Waitress service are running
   - Try accessing the application locally on the server first
   - Check Nginx logs for any connection errors

2. Common issues and solutions:
   - If you get a "Connection refused" error:
     - Verify Nginx is running: `C:\nginx\nginx.exe -t`
     - Check if port 80 is not being used by another application
   - If you get a "502 Bad Gateway" error:
     - Verify the Waitress service is running
     - Check the service logs in Windows Event Viewer
