<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>PIOM Dashboard</title>

<!-- React + Babel (para correr todo en un archivo) -->
<script src="https://unpkg.com/react@18/umd/react.development.js"></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

<style>
body { margin:0; background:#060a0f; font-family:sans-serif; color:#d8eaf8;}
.kpi { background:#0f1620; padding:15px; border:1px solid #1a2a3a; border-radius:6px; flex:1;}
.row { display:flex; gap:10px;}
.chat { background:#0b1018; padding:10px; height:300px; overflow:auto;}
input { width:100%; padding:8px; background:#0f1620; border:1px solid #1a2a3a; color:white;}
button { background:#00c8ff; border:none; padding:8px 12px; cursor:pointer;}
</style>
</head>

<body>
<div id="root"></div>

<script type="text/babel">

const AI_RESPONSES = {
  "¿Por qué bajó la producción?": "Cuello de botella en Sector B + falla en CA-12.",
  "¿Qué acción tomar ahora?": "Mover camiones y revisar CA-12."
};

function App(){
  const [messages, setMessages] = React.useState([
    {role:"ai", text:"Soy PIOM IA 🤖 ¿Qué necesitas analizar?"}
  ]);
  const [input, setInput] = React.useState("");

  const send = () => {
    if(!input) return;

    const userMsg = {role:"user", text:input};
    const aiMsg = {
      role:"ai",
      text: AI_RESPONSES[input] || "Analizando operación..."
    };

    setMessages([...messages, userMsg, aiMsg]);
    setInput("");
  };

  return (
    <div style={{padding:20}}>
      <h1 style={{color:"#00c8ff"}}>PIOM Dashboard</h1>

      {/* KPIs */}
      <div className="row">
        <div className="kpi">Producción: 47,820 ton</div>
        <div className="kpi">Ciclo: 38.4 min</div>
        <div className="kpi">Flota: 88%</div>
      </div>

      {/* Chat IA */}
      <h3 style={{marginTop:20}}>Asistente IA</h3>
      <div className="chat">
        {messages.map((m,i)=>(
          <div key={i} style={{
            textAlign: m.role==="user"?"right":"left",
            marginBottom:5
          }}>
            {m.text}
          </div>
        ))}
      </div>

      <div style={{display:"flex", gap:5, marginTop:10}}>
        <input
          value={input}
          onChange={e=>setInput(e.target.value)}
          placeholder="Pregunta algo..."
        />
        <button onClick={send}>Enviar</button>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);

</script>
</body>
</html>
