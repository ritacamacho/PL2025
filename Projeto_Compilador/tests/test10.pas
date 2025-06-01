program CafeLoop;

function PrepararParaProgramar: string;
var
  cafezinhos: integer;
begin
  cafezinhos := 0;

  writeln('Preparando o cérebro para codar...');

  while cafezinhos < 3 do
  begin
    writeln('Bebendo café número ', cafezinhos + 1, '...');
    cafezinhos := cafezinhos + 1;
  end;

  PrepararParaProgramar := 'Pronto! Modo programador ativado com sucesso!';
end;

begin
  writeln('Bom dia, programador!');
  writeln(PrepararParaProgramar);
  writeln('Agora sim, pode abrir o compilador.');
end.
