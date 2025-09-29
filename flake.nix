{
  description = "dangreco/comp370-hw05 environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs =
    inputs@{ flake-parts, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
        "x86_64-darwin"
      ];
      perSystem =
        {
          pkgs,
          ...
        }:
        let
          __zed = pkgs.writeTextFile {
            name = "zed-settings";
            text = builtins.toJSON {
              lsp = {
                ty = {
                  binary = {
                    path = "${pkgs.ty}/bin/ty";
                    arguments = [ "server" ];
                  };
                };
              };
              languages = {
                Python = {
                  language_servers = [
                    "!pylsp"
                    "!pyright"
                    "!basedpyright"
                    "ty"
                  ];
                  formatter = {
                    external = {
                      command = "${pkgs.ruff}/bin/ruff";
                      arguments = [
                        "format"
                        "--stdin-filename"
                        "{buffer_path}"
                      ];
                    };
                  };
                };
              };
            };
            destination = "/settings.json";
          };
        in

        {
          devShells.default = pkgs.mkShell {
            buildInputs = with pkgs; [
              openssl
            ];

            nativeBuildInputs = with pkgs; [
              nil
              nixd
              nixfmt
              just

              uv
              ty
              ruff
              python313

              __zed
            ];

            shellHook = ''
              echo ${__zed}
              rm -rf .zed
              mkdir -p .zed
              cp ${__zed}/settings.json .zed/settings.json
            '';
          };
        };
    };
}
