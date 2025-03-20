{pkgs}: {
  deps = [
    pkgs.postgresql
    pkgs.freetype
    pkgs.pango
    pkgs.harfbuzz
    pkgs.glib
    pkgs.ghostscript
    pkgs.fontconfig
    pkgs.glibcLocales
  ];
}
