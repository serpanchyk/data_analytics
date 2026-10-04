$out_dir = 'out';
$pdf_mode = 5;
$xelatex = 'xelatex -interaction=nonstopmode -halt-on-error %O %S';

END { system("cp $out_dir/*.pdf . 2>/dev/null") if defined $out_dir; }
