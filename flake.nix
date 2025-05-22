{
    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
        flake-utils.url = "github:numtide/flake-utils";

        chariot.url = "github:elysium-os/chariot";
        chariot.inputs.nixpkgs.follows = "nixpkgs";

        zed.url = "github:zed-industries/zed/main";
    };

    outputs = { nixpkgs, flake-utils, ... } @ inputs: flake-utils.lib.eachDefaultSystem (system:
        let
            pkgs = import nixpkgs { inherit system; };
            commonPackages = with pkgs; [
                inputs.chariot.defaultPackage.${system}

                wget # Required by Chariot
                libarchive # Required by Chariot

                python3 # Used heavily by tools

                gdb
                bochs
                qemu_full
                (pkgs.writeShellScriptBin "qemu-ovmf-x86-64" ''
                    ${pkgs.qemu_full}/bin/qemu-system-x86_64 \
                        -drive if=pflash,unit=0,format=raw,file=${pkgs.OVMF.fd}/FV/OVMF.fd,readonly=on \
                        "$@"
                '')
            ];
        in {
            devShells = {
                default = pkgs.mkShell {
                    shellHook = "export NIX_SHELL_NAME='elysium-os'";
                    nativeBuildInputs = commonPackages;
                };
                zed = pkgs.mkShell {
                    shellHook = "export NIX_SHELL_NAME='elysium-os/zed'";
                    nativeBuildInputs = commonPackages ++ [
                        inputs.zed.packages.${system}.default
                    ];
                };
            };
        }
    );
}
