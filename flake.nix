{
  description = "Entorno Curso ProgWeb";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};
    in
    {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = with pkgs; [
          # Backend & Frontend (Versiones actualizadas)
          python312
          starship
          python312Packages.django
          nodejs_20
          nodePackages.yarn

          # Infraestructura
          postgresql_15
          redis

          # Herramientas
          tmux neovim git curl
        ];

        shellHook = ''
          # Configuración de Postgres Local
          export PGDATA="$PWD/.postgres_data"
          export PGHOST="/tmp"

          # Inicialización automática de BD si no existe
          if [ ! -d "$PGDATA" ]; then
            initdb --auth=trust --no-locale --encoding=UTF8 > /dev/null
          fi

          # Alias de ayuda
          alias db-start="pg_ctl start -l $PGDATA/logfile -o '-k /tmp'"
          alias db-stop="pg_ctl stop"

          echo "--- Entorno de ProgWeb activado ---"
          echo "Python: $(python --version)"
          echo "Comandos: db-start (iniciar DB), db-stop (parar DB)"
        '';
      };
    };
}
