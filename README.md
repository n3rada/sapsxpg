Simplifying the usage of the [`SXPG_CALL_SYSTEM`](https://help.sap.com/saphelp_scm700_ehp01/helpdata/EN/4d/947a7c2cdb6c14e10000000a15822b/content.htm?no_cache=true) FM over a SAP server with logging.

## Requirement

The `NWRFCSDK` is proprietary SAP software, not open source. It requires an S-User account and specific permissions to download. Since SAP owns the intellectual property, it cannot be published or included inside this repository.

1. Visit the [SAP Support Portal](https://support.sap.com/en/product/connectors/nwrfcsdk.html).
2. Download the appropriate version for your operating system.
3. Follow the [installation guide](https://community.sap.com/t5/technology-blog-posts-by-members/connecting-python-with-sap-step-by-step-guide/ba-p/13452893).

If you already have `nwrfcsdk` dropped somewhere on your system, you can, in a Linux environment, find-it with:

```shell
find /opt /home /usr/local /srv -type d -path "*/nwrfcsdk" -print -quit 2>/dev/null
```

It will give you a path, use this one to export the two mandatory variables:
```shell
NWRFCSDK_PATH=$(find /opt /home /usr/local /srv -type d -path "*/nwrfcsdk" -print -quit 2>/dev/null | head -1)
export SAPNWRFC_HOME=$NWRFCSDK_PATH
export LD_LIBRARY_PATH="$NWRFCSDK_PATH/lib:"
```

## Installation

```shell
pipx install 'sapsxpg@git+https://github.com/n3rada/sapsxpg.git'
```

## Usage

```shell
sapsxpg 'aw01585632.aws.sap-noprod.example.com' 'SAPTEST' 'P@ass!w0rd/7'
```

## Remote Command Execution (RCE)

If the underlying system contains a command that allows you to execute commands on the remote system, you can connect it with [`toboggan`](https://github.com/n3rada/toboggan). First of all, generate the Remote Commande Execution proof of concept (PoC) with:
```shell
sapsxpg 'aw01585632.aws.sap-noprod.example.com' 'SAPTEST' 'P@ass!w0rd/7' --rce-poc "ZSH"
```

It will generate a file named `poc_aw01585632.aws.sap-noprod.example.com_ZSH.py`. Plug-it with `toboggan`:

```shell
toboggan -m poc_aw01585632.aws.sap-noprod.example.com_ZSH.py
```

## Disclaimer

This tool is intended for use in legal penetration testing, Capture The Flag (CTF) competitions, or other authorized and ethical security assessments.

Unauthorized use of this tool on systems you do not own or without proper authorization may be illegal. Please use-it responsibly and in compliance with applicable laws and regulations.


