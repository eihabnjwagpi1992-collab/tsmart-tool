{
  description = "Penumbra documentation (with Quartz & Obsidian)";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";

  outputs = {
    self,
    nixpkgs,
  }: {
    devShell.x86_64-linux = let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in
      pkgs.mkShell {
        packages = with pkgs; [
          nodejs_22
          pnpm
        ];

        shellHook = ''
          echo "Commands:"
          echo "  npx quartz build --serve  # Build and serve the documentation"
        '';
      };
  };
}
