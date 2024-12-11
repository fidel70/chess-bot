import autopep8

# Ruta al archivo Python que deseas corregir
input_file = "run-gui-with-reset.py"  # Cambia esto por el nombre de tu archivo
output_file = "run-gui-with-reset-modified.py"

# Leer el contenido del archivo original
with open(input_file, "r", encoding="utf-8") as file:
    original_code = file.read()

# Corregir la indentación y el formato
formatted_code = autopep8.fix_code(original_code, options={"aggressive": 1})

# Guardar el archivo corregido
with open(output_file, "w", encoding="utf-8") as file:
    file.write(formatted_code)

print(f"El archivo con indentación corregida se guardó como {output_file}.")
