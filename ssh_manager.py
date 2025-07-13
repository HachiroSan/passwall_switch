
import paramiko
import os
import socket
import requests
from datetime import datetime

class PassWallManager:
    """
    Handles SSH communication with the OpenWrt gateway to manage Pass Wall service.
    Provides methods to get status and toggle the service.
    """
    def __init__(self, host, user, port=22, password=None, key_file=None):
        """Initialize with SSH host, user, port, and optional password/key_file."""
        self.host = host
        self.user = user
        self.port = port
        self.password = password
        self.key_file = key_file
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _log(self, message, log_message=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] {message}"
        if log_message:
            log_message(formatted)

    def _connect(self, log_message=None):
        """Establish SSH connection. Returns True if successful, False otherwise."""
        try:
            connect_kwargs = {
                'hostname': self.host,
                'port': self.port,
                'username': self.user,
                'timeout': 8,  # Reduced timeout for faster failure
                'allow_agent': False,
                'look_for_keys': False
            }
            if self.key_file and os.path.exists(self.key_file):
                self._log(f"INFO: Attempting SSH connection to {self.user}@{self.host} using key file: {self.key_file}", log_message)
                connect_kwargs['key_filename'] = self.key_file
            elif self.password:
                self._log(f"INFO: Attempting SSH connection to {self.user}@{self.host} using password authentication.", log_message)
                connect_kwargs['password'] = self.password
            else:
                self._log(f"INFO: Attempting SSH connection to {self.user}@{self.host} without password or key file.", log_message)
                connect_kwargs['password'] = None
            self.client.connect(**connect_kwargs)
            self._log("SUCCESS: SSH connection established successfully.", log_message)
            return True
        except paramiko.ssh_exception.AuthenticationException as e:
            self._log(f"ERROR: Authentication failed: {e}. Please check your credentials in config.json.", log_message)
            return False
        except Exception as e:
            self._log(f"ERROR: Failed to connect: {e}", log_message)
            return False

    def _execute_command(self, command, log_message=None):
        """Execute a command over SSH. Returns (stdout, stderr)."""
        if not self.client.get_transport() or not self.client.get_transport().is_active():
            if not self._connect(log_message=log_message):
                return None, "Connection failed"
        try:
            self._log(f"INFO: Executing remote command: {command}", log_message)
            stdin, stdout, stderr = self.client.exec_command(command, timeout=10)  # Add timeout to command execution
            out = stdout.read().decode('utf-8')
            err = stderr.read().decode('utf-8')
            if err:
                self._log(f"ERROR: Command execution error: {err.strip()}", log_message)
            else:
                self._log(f"SUCCESS: Command executed successfully.", log_message)
            return out, err
        except Exception as e:
            self._log(f"ERROR: Exception during command execution: {e}", log_message)
            return None, str(e)

    def get_status(self, log_message=None):
        """Check if Pass Wall is running. Returns 'active', 'inactive', or 'error'."""
        command = "ps w | grep '[p]asswall'"
        stdout, stderr = self._execute_command(command, log_message=log_message)
        if stdout is None:
            return "error"
        if stdout.strip():
            return "active"
        return "inactive"

    def toggle_service(self, current_status, log_message=None):
        """Start or stop Pass Wall based on current_status. Returns 'ok' or 'error'."""
        action = "stop" if current_status == "active" else "start"
        command = f"/etc/init.d/passwall {action}"
        stdout, stderr = self._execute_command(command, log_message=log_message)
        if stderr or stdout is None:
            return "error"
        return "ok"

    def get_current_ip(self, log_message=None):
        """Get the current public IP address using external service. Returns IP string or 'error'."""
        try:
            self._log("INFO: Attempting to get external IP address from api.ipify.org", log_message)
            response = requests.get("https://api.ipify.org", timeout=5)
            if response.status_code == 200:
                ip = response.text.strip()
                # Basic IP validation
                if self._is_valid_ip(ip):
                    self._log(f"SUCCESS: Retrieved current public IP address: {ip}", log_message)
                    return ip
                else:
                    self._log(f"WARNING: Invalid IP format received: {ip}", log_message)
                    return "error"
            else:
                self._log(f"WARNING: Service returned status code: {response.status_code}", log_message)
                return "error"
        except requests.exceptions.RequestException as e:
            self._log(f"ERROR: No internet connection or service unavailable: {e}", log_message)
            # Fallback: try to get local IP if no internet
            self._log("INFO: Attempting fallback to local IP address", log_message)
            local_ip = self.get_local_ip(log_message)
            if local_ip != "error":
                self._log(f"SUCCESS: Retrieved local IP address as fallback: {local_ip}", log_message)
                return f"{local_ip} (local)"
            else:
                self._log("ERROR: Failed to retrieve both external and local IP addresses", log_message)
                return "error"
        except Exception as e:
            self._log(f"ERROR: Unexpected error getting external IP: {e}", log_message)
            return "error"

    def get_local_ip(self, log_message=None):
        """Get the local IP address of the current Windows machine. Returns IP string or 'error'."""
        try:
            # Get local IP by connecting to a remote address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))  # Connect to Google DNS
            local_ip = s.getsockname()[0]
            s.close()
            
            if self._is_valid_ip(local_ip):
                self._log(f"SUCCESS: Retrieved local IP address: {local_ip}", log_message)
                return local_ip
            else:
                self._log(f"WARNING: Invalid local IP format: {local_ip}", log_message)
                return "error"
        except Exception as e:
            self._log(f"ERROR: Failed to retrieve local IP address: {e}", log_message)
            return "error"

    def _is_valid_ip(self, ip):
        """Basic validation for IP address format."""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not part.isdigit() or not 0 <= int(part) <= 255:
                    return False
            return True
        except:
            return False

    def close(self, log_message=None):
        """Close the SSH connection."""
        if self.client:
            try:
                # Close the transport immediately to avoid hanging
                if self.client.get_transport():
                    self.client.get_transport().close()
                self.client.close()
                self._log("INFO: SSH connection closed.", log_message)
            except Exception as e:
                self._log(f"WARNING: Error closing SSH connection: {e}", log_message)
