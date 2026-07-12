:top
@exe\wasm3 genasm/%1.asm world/%1.wr3
@if errorlevel 1 goto err
@shift 
@if not "%1" == "." goto top
:err
