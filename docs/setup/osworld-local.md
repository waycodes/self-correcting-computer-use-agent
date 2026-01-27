# OSWorld Local Setup (VMware/VirtualBox)

This guide covers setting up OSWorld with local virtualization for development.

## Prerequisites

- 16GB+ RAM (32GB recommended)
- 50GB+ free disk space
- VMware Workstation/Fusion or VirtualBox 7.0+
- Python 3.10+

## Option 1: VMware (Recommended)

### 1. Install VMware

**Linux:**
```bash
# Download VMware Workstation Pro from vmware.com
chmod +x VMware-Workstation-*.bundle
sudo ./VMware-Workstation-*.bundle
```

**macOS:**
```bash
# Download VMware Fusion from vmware.com
# Install via DMG
```

### 2. Download OSWorld VM Image

```bash
# Clone OSWorld repository
git clone https://github.com/xlang-ai/OSWorld.git
cd OSWorld

# Download VM image (Ubuntu 22.04)
python -m desktop_env.providers.vmware.download_vm
```

### 3. Configure VM

Edit `desktop_env/providers/vmware/config.yaml`:
```yaml
vm_path: /path/to/osworld-ubuntu.vmx
snapshot_name: "clean_state"
headless: false  # Set true for CI
```

### 4. Verify Setup

```bash
python -c "from desktop_env import DesktopEnv; env = DesktopEnv(); print('OK')"
```

## Option 2: VirtualBox

### 1. Install VirtualBox

```bash
# Ubuntu/Debian
sudo apt install virtualbox virtualbox-ext-pack

# macOS
brew install --cask virtualbox virtualbox-extension-pack
```

### 2. Import OSWorld OVA

```bash
# Download OVA from OSWorld releases
VBoxManage import osworld-ubuntu.ova --vsys 0 --vmname "osworld"
```

### 3. Configure VM

```bash
# Enable nested virtualization if needed
VBoxManage modifyvm "osworld" --nested-hw-virt on

# Set memory and CPUs
VBoxManage modifyvm "osworld" --memory 8192 --cpus 4
```

## Troubleshooting

**VM won't start:**
- Check virtualization is enabled in BIOS (VT-x/AMD-V)
- Ensure no other hypervisor is running

**Slow performance:**
- Allocate more RAM/CPUs to VM
- Use SSD for VM storage
- Enable 3D acceleration

## Next Steps

After setup, verify with:
```bash
sca doctor --check osworld
```
