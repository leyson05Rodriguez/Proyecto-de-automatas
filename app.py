from flask import Flask, render_template, request
import re

app = Flask(__name__)

# Expresión regular principal (validación completa)
regex_pattern = r"^(What|Where|When|Why|Who|Whom|Which|Whose|How)\s+(was|were)(n't| not)?\s+(I|you|he|she|it|we|they|[a-zA-Z]+)\s+[a-zA-Z]+ing\?$"

# 🔧 Función para normalizar la pregunta
def normalizar_pregunta(pregunta):
    # Elimina espacios antes de signos de puntuación
    pregunta = re.sub(r"\s+([?.!])", r"\1", pregunta)
    # Elimina espacios extra al principio y final
    return pregunta.strip()

# Función de validación detallada
def validar_pregunta(pregunta):
    errores = []
    sugerencia = ""

    if not pregunta:
        errores.append("La pregunta está vacía.")
        sugerencia = "Escribe una pregunta WH en pasado continuo negativo."
        return errores, sugerencia

    if not re.search(r"^(What|Where|When|Why|Who|Whom|Which|Whose|How)\b", pregunta, re.IGNORECASE):
        errores.append("Falta una palabra con WH (What, Where, Why, etc.).")
        sugerencia = "Agrega una palabra con WH al inicio de la pregunta."

    if not re.search(r"\b(was|were|wasn't|weren't)\b", pregunta, re.IGNORECASE):
        errores.append("Falta el verbo 'to be' (was/were).")
        sugerencia = "Incluye 'was not', 'were not', 'wasn't' o 'weren't' después de la palabra con WH."

    if not re.search(r"\b[a-zA-Z]+ing\b", pregunta):
        errores.append("Falta un verbo terminado en -ing.")
        sugerencia = "Agrega un verbo terminado en -ing (e.g., studying)."

    if not pregunta.strip().endswith("?"):
        errores.append("Falta el signo de interrogación al final.")
        sugerencia = "Termina la pregunta con un signo de interrogación (?)."

    # Validación gramatical auxiliar-sujeto
    match = re.search(r"\b(was not|were not|wasn't|weren't)\b\s+([a-zA-Z]+)", pregunta, re.IGNORECASE)
    if match:
        auxiliar = match.group(1).lower()
        sujeto = match.group(2).lower()
        if auxiliar in ["was not", "wasn't"] and sujeto not in ["i", "he", "she", "it"]:
            errores.append(f"'{auxiliar}' no se usa con '{sujeto}'.")
            sugerencia = f"Usa 'wasn't' con I/he/she/it."
        elif auxiliar in ["were not", "weren't"] and sujeto not in ["you", "we", "they"]:
            errores.append(f"'{auxiliar}' no se usa con '{sujeto}'.")
            sugerencia = f"Usa 'weren't' con you/we/they."

    return errores, sugerencia

@app.route("/", methods=["GET", "POST"])
def index():
    questions = [""] * 5
    errors = [[] for _ in range(5)]
    suggestions = [""] * 5
    score = None
    correct_flags = [False] * 5

    if request.method == "POST":
        questions = [request.form.get(f"question{i+1}", "") for i in range(5)]
        score = 0
        for i, question in enumerate(questions):
            clean_q = normalizar_pregunta(question)
            if re.match(regex_pattern, clean_q):
                errores, _ = validar_pregunta(clean_q)
                if not errores:
                    score += 1
                    correct_flags[i] = True
                else:
                    errors[i] = errores
            else:
                errores, sugerencia = validar_pregunta(clean_q)
                errors[i] = errores
                suggestions[i] = sugerencia

    return render_template("index.html", questions=questions, errors=errors, suggestions=suggestions, score=score, correct_flags=correct_flags)

if __name__ == "__main__":
    app.run(debug=True)