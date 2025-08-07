#!/usr/bin/env python3
"""
Test script to connect to NAS using SMB protocol
"""

from smb.SMBConnection import SMBConnection
import tempfile
import os

def test_nas_connection():
    """Test connection to NAS server"""
    
    # NAS connection details
    nas_ip = "192.168.0.94"
    share_names = ["Guruukul_DB", "Data-All-User"]
    
    # Try different authentication methods
    auth_methods = [
        {"username": "", "password": "", "domain": ""},  # Anonymous
        {"username": "guest", "password": "", "domain": ""},  # Guest
        {"username": "everyone", "password": "", "domain": ""},  # Everyone
        {"username": "anonymous", "password": "", "domain": ""},  # Anonymous user
        {"username": "", "password": "", "domain": "WORKGROUP"},  # Anonymous with domain
        {"username": "guest", "password": "", "domain": "WORKGROUP"},  # Guest with domain
        {"username": "everyone", "password": "", "domain": "WORKGROUP"},  # Everyone with domain
    ]
    
    for i, auth in enumerate(auth_methods):
        print(f"\nTrying method {i+1}: {auth}")

        try:
            # Create SMB connection
            conn = SMBConnection(
                username=auth["username"],
                password=auth["password"],
                my_name="BHIV-Client",
                remote_name="NAS",
                domain=auth["domain"],
                use_ntlm_v2=True,
                is_direct_tcp=True
            )

            # Try to connect
            print(f"Attempting to connect to {nas_ip}...")
            result = conn.connect(nas_ip, 445)

            if result:
                print("✅ Connection successful!")

                # Try to list shares
                try:
                    shares = conn.listShares()
                    print("Available shares:")
                    for share in shares:
                        print(f"  - {share.name}: {share.comments}")

                    # Try to access Guruukul_DB specifically with different approaches
                    share_name = "Guruukul_DB"

                    # Method 1: Direct path access
                    try:
                        files = conn.listPath(share_name, "/")
                        print(f"\n🎉 SUCCESS! Can access {share_name} share")
                        print(f"Files in {share_name}:")
                        for file in files[:10]:  # Show first 10 files
                            print(f"  - {file.filename} ({'DIR' if file.isDirectory else 'FILE'})")
                        conn.close()
                        return True

                    except Exception as e1:
                        print(f"❌ Method 1 failed for {share_name}: {e1}")

                        # Method 2: Try with different path formats
                        for path_format in ["", ".", "/"]:
                            try:
                                files = conn.listPath(share_name, path_format)
                                print(f"\n🎉 SUCCESS! Can access {share_name} with path '{path_format}'")
                                print(f"Files in {share_name}:")
                                for file in files[:10]:
                                    print(f"  - {file.filename} ({'DIR' if file.isDirectory else 'FILE'})")
                                conn.close()
                                return True
                            except Exception as e2:
                                print(f"❌ Path '{path_format}' failed: {e2}")

                except Exception as e:
                    print(f"❌ Cannot list shares: {e}")

                conn.close()

            else:
                print("❌ Connection failed")

        except Exception as e:
            print(f"❌ Connection error: {e}")
    
    print("\n❌ All connection methods failed")
    return False

if __name__ == "__main__":
    print("Testing NAS connection...")
    test_nas_connection()
