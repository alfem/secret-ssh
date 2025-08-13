#!/usr/bin/env python3

import csv
import pexpect
import sys
import os
import argparse
from getpass import getpass

def load_servers(csv_file):
    """Load servers from CSV file"""
    servers = []
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                servers.append({
                    'numero': row['Numero'],
                    'ip': row['IP'],
                    'nombre': row['Nombre']
                })
    except FileNotFoundError:
        print(f"Error: File {csv_file} not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        sys.exit(1)
    
    return servers

def display_servers(servers):
    """Display list of available servers"""
    print("\n" + "="*60)
    print("AVAILABLE SERVERS")
    print("="*60)
    for i, server in enumerate(servers, 1):
        print(f"{i:2d}. {server['nombre']} ({server['ip']}) - Secret #{server['numero']}")
    print("="*60)

def select_server(servers):
    """Allow user to select a server"""
    while True:
        try:
            choice = input(f"\nSelect a server (1-{len(servers)}) or 'q' to quit: ").strip()
            if choice.lower() == 'q':
                print("Exiting...")
                sys.exit(0)
            
            index = int(choice) - 1
            if 0 <= index < len(servers):
                return servers[index]
            else:
                print(f"Please enter a number between 1 and {len(servers)}")
        except ValueError:
            print("Please enter a valid number")

def get_credentials(ss_user, ss_server):
    """Get user credentials"""
    print("\n" + "-"*40)
    print("SECRET SERVER CREDENTIALS")
    print("-"*40)
    print(f"User: {ss_user}")
    print(f"Server: {ss_server}")
    password = getpass("Password: ")
    pin = input("PIN (OTP): ").strip()
    
    return password, pin

def connect_ssh(server, ss_user, ss_server, ss_password, ss_pin):
    """Connect via SSH using Secret Server as proxy"""
    
    print(f"\nConnecting to {server['nombre']} ({server['ip']}) via Secret Server...")
    print(f"Target ID: {server['numero']}")
    
    # SSH Command: ssh myuser@secretserver -p 22 -t launch target-id
    ssh_cmd = f"ssh {ss_user}@{ss_server} -p 22 -t launch {server['numero']}"
    
    print(f"\nSSH Command:")
    print(f"  {ssh_cmd}")
    print("\nPress Ctrl+C to cancel\n")
    
    try:
        
        # Start SSH session
        child = pexpect.spawn(ssh_cmd, timeout=30)
        # child.logfile_read = sys.stdout.buffer  # Commented to avoid duplicate output
        
        # Expected patterns
        patterns = [
            'Are you sure you want to continue connecting',
            'password:',
            'Password:',
            'Pin code:',
            'PIN:',
            pexpect.TIMEOUT,
            pexpect.EOF
        ]
        
        while True:
            index = child.expect(patterns)
            
            if index == 0:  # Host key confirmation
                child.sendline('yes')
                continue
                
            elif index in [1, 2]:  # Password prompt
                child.sendline(ss_password)
                continue
                
            elif index in [3, 4]:  # PIN/Pin code prompt
                child.sendline(ss_pin)
                break  # After PIN, transfer control
                
            elif index == 5:  # Timeout
                print("\nTimeout waiting for server response")
                return
                
            elif index == 6:  # EOF
                print("\nConnection terminated")
                return
        
        # Transfer control to user
        print(f"\n{'='*50}")
        print("SSH SESSION ESTABLISHED")
        print("Press Ctrl+] to exit session")
        print(f"{'='*50}\n")
        
        child.interact()
        
    except pexpect.exceptions.TIMEOUT:
        print(f"\nTimeout connecting via Secret Server")
    except pexpect.exceptions.EOF:
        print(f"\nConnection closed by Secret Server")
    except KeyboardInterrupt:
        print(f"\nConnection cancelled by user")
    except Exception as e:
        print(f"\nError during connection: {e}")
    finally:
        try:
            child.close()
        except:
            pass

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="SSH Auto-Connect with Secret Server",
        epilog="Example: python secret-ssh.py -u myuser -s secretserver.company.com"
    )
    
    parser.add_argument(
        '-u', '--user',
        required=True,
        help='Secret Server user'
    )
    
    parser.add_argument(
        '-s', '--server',
        required=True,
        help='Secret Server hostname'
    )
    
    parser.add_argument(
        '-c', '--csv',
        default='output.csv',
        help='CSV file with servers (default: output.csv)'
    )
    
    return parser.parse_args()

def main():
    """Main function"""
    
    # Parse arguments
    args = parse_arguments()
    
    print("="*60)
    print("SSH AUTO-CONNECT WITH SECRET SERVER")
    print("="*60)
    print(f"Secret Server User: {args.user}")
    print(f"Secret Server Host: {args.server}")
    print("="*60)
    
    # Check if CSV file exists
    if not os.path.exists(args.csv):
        print(f"Error: File {args.csv} not found")
        print("Run extract_links.py first to generate the CSV file")
        sys.exit(1)
    
    # Load servers
    servers = load_servers(args.csv)
    if not servers:
        print("No servers found in CSV file")
        sys.exit(1)
    
    # Main loop
    while True:
        display_servers(servers)
        selected_server = select_server(servers)
        
        print(f"\nSelected server: {selected_server['nombre']} ({selected_server['ip']})")
        print(f"Secret Number: {selected_server['numero']}")
        
        # Get credentials
        ss_password, ss_pin = get_credentials(args.user, args.server)
        
        # Connect
        connect_ssh(selected_server, args.user, args.server, ss_password, ss_pin)
        
        # Ask if user wants to connect to another server
        another = input("\nConnect to another server? (y/N): ").strip().lower()
        if another not in ['y', 'yes', 's', 'si', 'sí']:
            print("Goodbye!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nScript interrupted by user")
        sys.exit(0)