{
    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";
        flake-utils.url = "github:numtide/flake-utils";

        chariot.url = "github:elysium-os/chariot";
        chariot.inputs.nixpkgs.follows = "nixpkgs";
    };

    outputs =
        { nixpkgs, flake-utils, ... }@inputs:
        flake-utils.lib.eachDefaultSystem (
            system:
            let
                pkgs = import nixpkgs { inherit system; };
                commonPackages = with pkgs; [
                    inputs.chariot.defaultPackage.${system}

                    wget # Required by Chariot
                    libarchive # Required by Chariot

                    python3 # Required by scripts

                    # Required by initsys scripts
                    python313Packages.pyelftools
                    python313Packages.libclang
                    python313Packages.pyvis
                    python313Packages.networkx
                    python313Packages.termcolor

                    llvmPackages_20.clang-tools # clang-format & clang-tidy

                    gdb
                    bochs
                    qemu_full
                    (pkgs.writeShellScriptBin "qemu-ovmf-x86-64" ''
                        ${pkgs.qemu_full}/bin/qemu-system-x86_64 \
                            -drive if=pflash,unit=0,format=raw,file=${pkgs.OVMF.fd}/FV/OVMF.fd,readonly=on \
                            "$@"
                    '')
                ];
            in
            {
                devShells.default = pkgs.mkShell {
                    shellHook = "export NIX_SHELL_NAME='elysium-os'";
                    nativeBuildInputs = commonPackages;
                };
            }
        );
}
