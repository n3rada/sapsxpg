# 🏢 sapsxpg

Simplify the usage of the [`SXPG_CALL_SYSTEM`](https://help.sap.com/saphelp_scm700_ehp01/helpdata/EN/4d/947a7c2cdb6c14e10000000a15822b/content.htm?no_cache=true) function module over a SAP server with logging.

`sapsxpg` connects to a SAP system via RFC, enumerates available external OS commands registered in `SM49`/`SM69`, and provides an interactive shell to execute them. It also auto-detects the remote operating system and can generate [toboggan](https://github.com/n3rada/toboggan)-compatible RCE proof-of-concept scripts.

> [!TIP]
> If the SAP system has a command that allows arbitrary execution (e.g., `ZSH`, `ZBASH`), you can generate a PoC with `--rce-poc` and plug it into [toboggan](https://github.com/n3rada/toboggan) for a full semi-interactive shell.

## ⚙️ Prerequisite

The [`NWRFCSDK`](https://support.sap.com/en/product/connectors/nwrfcsdk.html) is proprietary SAP software. It requires an S-User account and specific permissions to download. Since SAP owns the intellectual property, it cannot be published or included inside this repository.

1. Visit the [SAP Support Portal](https://support.sap.com/en/product/connectors/nwrfcsdk.html).
2. Download the appropriate version for your operating system.
3. Follow the [installation guide](https://community.sap.com/t5/technology-blog-posts-by-members/connecting-python-with-sap-step-by-step-guide/ba-p/13452893).

If you already have `nwrfcsdk` dropped somewhere on your system, you can locate and export the mandatory variables:

```shell
NWRFCSDK_PATH=$(find /opt /home /usr/local /srv -type d -path "*/nwrfcsdk" -print -quit 2>/dev/null | head -1)
export SAPNWRFC_HOME=$NWRFCSDK_PATH
export LD_LIBRARY_PATH="$NWRFCSDK_PATH/lib:"
```

> [!NOTE]
> `pyrfc` is not declared as a hard dependency because it requires the proprietary NWRFCSDK to build. You must install it separately after setting up the SDK.

## 📦 Installation

Prefer using [`uv`](https://docs.astral.sh/uv/), a fast Python package manager that installs tools in isolated environments. Alternatively, [`pipx`](https://pypa.github.io/pipx/) or `pip` work as well.

### With [uv](https://docs.astral.sh/uv/) (recommended)

[`uv tool install`](https://docs.astral.sh/uv/guides/tools/#installing-tools) persistently installs the tool and adds it to your `PATH`, similar to `pipx`:

```bash
uv tool install git+https://github.com/n3rada/sapsxpg.git --with pyrfc==3.3.1
```

After installation, `sapsxpg` is available directly:

```bash
sapsxpg --help
```

To upgrade later:

```bash
uv tool upgrade sapsxpg
```

> [!TIP]
> You can also run `sapsxpg` **without installing** it using [`uvx`](https://docs.astral.sh/uv/guides/tools/#running-tools) (alias for `uv tool run`), which creates a temporary isolated environment on the fly:
> ```bash
> uvx --from git+https://github.com/n3rada/sapsxpg.git --with pyrfc==3.3.1 sapsxpg --help
> ```

### With pipx or pip

```bash
pipx install 'git+https://github.com/n3rada/sapsxpg.git'
pipx inject sapsxpg pyrfc==3.3.1
```

```bash
pip install 'git+https://github.com/n3rada/sapsxpg.git'
pip install pyrfc==3.3.1
```

## 🧸 Usage

```shell
sapsxpg <target> <username> <password> [options]
```

### ⚡ Quickstart

```shell
# Direct connection (default system number 00, client 500)
sapsxpg sap-server.example.com SAPUSER 'P@ssw0rd!'

# Custom client and system number
sapsxpg sap-server.example.com SAPUSER 'P@ssw0rd!' -c 100 -s 01

# Load-balanced connection via Message Server
sapsxpg sap-server.example.com SAPUSER 'P@ssw0rd!' -m msgserver -r PRD -g PUBLIC
```

### 🔗 Connection Modes

| Flag | Description |
|------|-------------|
| `-c`, `--client` | SAP client number (default: `500`) |
| `-s`, `--sysnr` | System number for direct connection (default: `00`) |
| `-m`, `--mshost` | Message server hostname (load-balanced mode) |
| `-r`, `--r3name` | SAP system ID, required with `-m` |
| `-g`, `--group` | Logon group, required with `-m` |
| `-t`, `--timeout` | Connection timeout in seconds (default: `30`) |
| `--no-trace` | Disable SAP RFC trace logging |
| `--os` | Force OS filter: `linux`, `windows`, `unix`, `all`, `anyos` |

### 🔍 Interactive Shell

Once connected, `sapsxpg` drops you into an interactive shell with tab completion and command history. The shell supports:

- **Built-in commands**: `ls`, `cat`, `ps`, `env`
- **SAP-registered commands**: any command registered in `SM49`/`SM69`
- **Help**: type `h`, `help`, or `?` to list all available commands

The tool auto-detects the remote OS and filters commands accordingly. Results are cached locally for faster subsequent sessions.

## 🎯 RCE Proof of Concept

Generate a [toboggan](https://github.com/n3rada/toboggan)-compatible RCE module from any SAP command that allows execution:

```shell
sapsxpg sap-server.example.com SAPUSER 'P@ssw0rd!' --rce-poc ZSH
```

This produces a `poc_sap-server.example.com_ZSH.py` file. Plug it into toboggan for a full semi-interactive shell:

```shell
toboggan poc_sap-server.example.com_ZSH.py
```

> [!NOTE]
> The generated PoC handles the 128-character argument limit of `SXPG_CALL_SYSTEM` by base64-encoding the command and using `${IFS}` for space substitution.

## ⚠️ Disclaimer

**This tool is provided strictly for defensive security research, education, and authorized penetration testing.** You must have **explicit written authorization** before running this software against any system you do not own.

Acceptable environments include:
- Private lab environments you control (local VMs, isolated networks).
- Sanctioned learning platforms (CTFs, Hack The Box, OffSec exam scenarios).
- Formal penetration-test or red-team engagements with documented customer consent.

Misuse of this project may result in legal action.

## ⚖️ Legal Notice

Any unauthorized use of this tool in real-world environments or against systems without explicit permission from the system owner is strictly prohibited and may violate legal and ethical standards. The creators and contributors of this tool are not responsible for any misuse or damage caused.

Use responsibly and ethically. Always respect the law and obtain proper authorization.


