import { useState, useEffect, useRef } from "react";

const C = {
  bg: "#060a0f", panel: "#0b1018", card: "#0f1620", hover: "#141d2a",
  border: "#1a2a3a", borderB: "#1e3a5a",
  accent: "#00c8ff", gold: "#f0a500", green: "#00e87a",
  danger: "#ff3d5a", warn: "#ff9f1c", purple: "#a855f7",
  text: "#d8eaf8", textS: "#6a8faa", textD: "#3a5570",
};

const css = `
  @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  ::-webkit-scrollbar{width:4px;height:4px;}
  ::-webkit-scrollbar-track{background:transparent;}
  ::-webkit-scrollbar-thumb{background:#1a2a3a;border-radius:2px;}
  @keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}
  @keyframes pulse{0%,100%{filter:drop-shadow(0 0 6px rgba(0,200,255,.5))}50%{filter:drop-shadow(0 0 16px rgba(0,200,255,.9))}}
  @keyframes msgIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
  @keyframes nodePulse{0%,100%{box-shadow:0 0 0 0 rgba(0,200,255,.4)}50%{box-shadow:0 0 0 8px rgba(0,200,255,0)}}
  @keyframes truckMove{0%{opacity:.7}50%{opacity:1}100%{opacity:.7}}
  @keyframes spin{to{transform:rotate(360deg)}}
  .msg-in{animation:msgIn .3s ease;}
  .blink{animation:blink 2s infinite;}
  .pulse{animation:pulse 3s ease-in-out infinite;}
  .nav-btn{transition:all .2s;cursor:pointer;}
  .nav-btn:hover{color:#d8eaf8!important;border-color:#1e3a5a!important;background:#141d2a!important;}
  .nav-btn.active{color:#00c8ff!important;border-color:#00c8ff!important;background:rgba(0,200,255,.05)!important;}
  .sidebar-item{transition:all .15s;cursor:pointer;border-left:2px solid transparent;}
  .sidebar-item:hover{background:#141d2a!important;color:#d8eaf8!important;}
  .sidebar-item.active{background:rgba(0,200,255,.06)!important;border-left-color:#00c8ff!important;color:#00c8ff!important;}
  .kpi-card{transition:border-color .2s;}
  .kpi-card:hover{border-color:#1e3a5a!important;}
  .fleet-cell{transition:transform .15s;cursor:pointer;}
  .fleet-cell:hover{transform:scale(1.12);}
  .quick-btn{transition:all .15s;cursor:pointer;text-align:left;}
  .quick-btn:hover{background:#141d2a!important;border-color:#00c8ff!important;color:#00c8ff!important;}
  .send-btn{transition:all .15s;cursor:pointer;}
  .send-btn:hover{background:#33d4ff!important;box-shadow:0 0 14px rgba(0,200,255,.4)!important;}
  .eq-row:hover td{background:#141d2a!important;}
  .truck-dot{animation:truckMove 2s ease-in-out infinite;}
`;

const F = { title: "'Rajdhani', sans-serif", mono: "'Share Tech Mono', monospace", body: "'Exo 2', sans-serif" };

const AI_RESPONSES = {
  "¿Por qué bajó la producción?": {
    text: "Analicé los datos del turno actual. La producción bajó por dos factores principales:\n\n🔴 Cuello de botella en Sector B: Cola de 8+ camiones esperando PALA-03, causando 18 min de tiempo muerto acumulado.\n\n🔴 Ciclo extendido CA-12: 52 min/ciclo (+48% sobre objetivo), posible falla mecánica en transmisión.\n\nEstos dos factores explican el 73% de la brecha productiva.",
    data: [{ k: "Pérdida estimada", v: "~4,180 ton" }, { k: "Factor Sector B", v: "61% del impacto" }, { k: "Factor CA-12", v: "12% del impacto" }]
  },
  "¿Qué equipo genera más retraso?": {
    text: "CA-12 es el equipo con mayor impacto negativo actualmente:\n\n• Ciclo promedio actual: 52 min (objetivo ≤35 min)\n• Solo 3 ciclos completados en últimas 2 horas\n• Impacto estimado: -840 ton bajo contribución esperada\n\nRecomiendo asignarlo a ruta más corta o enviarlo a revisión técnica preventiva.",
    data: [{ k: "Equipo crítico", v: "CA-12" }, { k: "Ciclo actual", v: "52 min" }, { k: "Ciclo normal", v: "34 min" }, { k: "Pérdida", v: "~840 ton" }]
  },
  "Mejor asignación de camiones": {
    text: "Basado en estado actual, recomiendo esta reasignación inmediata:\n\n1. Mover 3 camiones de Sector B (cola activa) a Sector A — PALA-01 y PALA-02 tienen capacidad libre.\n\n2. CA-17 (en espera) → asignar a ruta Sector C, PALA-05 está sub-utilizada.\n\n3. CA-12 → retirar de operación y evaluar técnicamente.\n\nEsto recuperaría ~1,200 ton en las próximas 2 horas.",
    data: [{ k: "Ganancia estimada", v: "+1,200 ton" }, { k: "Equipos a reasignar", v: "4 camiones" }, { k: "Tiempo implementar", v: "~8 min" }]
  },
  "¿Qué acción tomar ahora?": {
    text: "Prioridades por impacto inmediato:\n\n🔴 URGENTE (ahora):\n1. Descongestionar Sector B → redirigir 3 camiones a Sector A\n2. Enviar CA-12 a inspección técnica\n\n🟡 IMPORTANTE (próxima hora):\n3. Activar CA-17 → asignar a PALA-05 Sector C\n4. Revisar rendimiento PALA-04 (bajo histórico)\n\nImplementando estas acciones se estima recuperar el 68% de la brecha productiva antes del fin de turno.",
    data: [{ k: "Recuperación estimada", v: "+2,840 ton" }, { k: "Cumplimiento meta", v: "98.7% proyectado" }]
  }
};

const EQUIP = [
  { id: "PALA-01", st: "op", sector: "A", ciclos: 2.8, carga: 94, tonhr: 1420 },
  { id: "PALA-02", st: "op", sector: "A", ciclos: 2.6, carga: 88, tonhr: 1310 },
  { id: "PALA-03", st: "op", sector: "B", ciclos: 2.9, carga: 96, tonhr: 1480 },
  { id: "PALA-04", st: "op", sector: "B", ciclos: 2.1, carga: 72, tonhr: 1050 },
  { id: "PALA-05", st: "op", sector: "C", ciclos: 2.7, carga: 91, tonhr: 1390 },
  { id: "PALA-06", st: "maint", sector: "—", ciclos: 0, carga: 0, tonhr: 0 },
];

const PROD_DATA = [5100, 5320, 5480, 5290, 4980, 5150, 4820, 4650, 4710];
const PROD_LABELS = ["07:00","08:00","09:00","10:00","11:00","12:00","13:00","14:00","15:00"];

// ── Mini sparkline bars ──
function Spark({ data, color }) {
  const max = Math.max(...data);
  return (
    <div style={{ display: "flex", alignItems: "flex-end", gap: 2, height: 24, marginTop: 6 }}>
      {data.map((v, i) => (
        <div key={i} style={{
          flex: 1, height: `${(v / max) * 100}%`, borderRadius: "2px 2px 0 0",
          background: i === data.length - 1 ? color : `${color}33`,
          transition: "height .5s"
        }} />
      ))}
    </div>
  );
}

// ── KPI Card ──
function KpiCard({ label, value, unit, delta, deltaUp, color, sparkData, topColor }) {
  return (
    <div className="kpi-card" style={{
      background: C.card, border: `1px solid ${C.border}`, borderRadius: 4,
      padding: "12px 14px", position: "relative", overflow: "hidden", flex: 1
    }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: topColor }} />
      <div style={{ fontSize: 9, letterSpacing: "1.5px", textTransform: "uppercase", color: C.textD, marginBottom: 5, fontFamily: F.body }}>{label}</div>
      <div style={{ fontFamily: F.title, fontSize: 26, fontWeight: 700, color, lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 11, color: C.textS, fontFamily: F.body, marginTop: 2 }}>{unit}</div>
      <div style={{ fontSize: 10, fontFamily: F.mono, color: deltaUp ? C.green : C.danger, marginTop: 3 }}>{deltaUp ? "▲" : "▼"} {delta}</div>
      <Spark data={sparkData} color={topColor} />
    </div>
  );
}

// ── Production Chart ──
function ProdChart() {
  const canvasRef = useRef(null);
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const W = canvas.offsetWidth || 500;
    const H = 100;
    canvas.width = W; canvas.height = H;
    const pad = { l: 32, r: 10, t: 12, b: 4 };
    const cw = W - pad.l - pad.r, ch = H - pad.t - pad.b;
    const min = 4000, max = 6000, target = 5200;

    ctx.clearRect(0, 0, W, H);
    // Grid
    for (let i = 0; i <= 4; i++) {
      const y = pad.t + (ch / 4) * i;
      ctx.strokeStyle = "rgba(26,42,58,0.8)"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(W - pad.r, y); ctx.stroke();
    }
    // Target
    const ty = pad.t + ch * (1 - (target - min) / (max - min));
    ctx.strokeStyle = "rgba(240,165,0,0.5)"; ctx.setLineDash([4, 4]); ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(pad.l, ty); ctx.lineTo(W - pad.r, ty); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = "rgba(240,165,0,0.8)"; ctx.font = "9px 'Share Tech Mono'";
    ctx.fillText("META 5.2k", pad.l + 3, ty - 3);

    const pts = PROD_DATA.map((v, i) => ({
      x: pad.l + (cw / (PROD_DATA.length - 1)) * i,
      y: pad.t + ch * (1 - (v - min) / (max - min))
    }));

    // Area
    const grad = ctx.createLinearGradient(0, pad.t, 0, H);
    grad.addColorStop(0, "rgba(0,200,255,0.2)"); grad.addColorStop(1, "rgba(0,200,255,0.01)");
    ctx.beginPath();
    ctx.moveTo(pts[0].x, H - pad.b);
    pts.forEach(p => ctx.lineTo(p.x, p.y));
    ctx.lineTo(pts[pts.length - 1].x, H - pad.b);
    ctx.closePath(); ctx.fillStyle = grad; ctx.fill();

    // Line
    ctx.beginPath(); ctx.strokeStyle = "rgba(0,200,255,.9)"; ctx.lineWidth = 2;
    pts.forEach((p, i) => i === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y));
    ctx.stroke();

    // Dots
    pts.forEach((p, i) => {
      ctx.beginPath(); ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
      ctx.fillStyle = PROD_DATA[i] >= target ? "#00e87a" : "#ff3d5a";
      ctx.fill();
      ctx.strokeStyle = "rgba(0,0,0,.5)"; ctx.lineWidth = 1; ctx.stroke();
    });

    // Y labels
    [6000, 5500, 5000, 4500, 4000].forEach((v, i) => {
      ctx.fillStyle = "rgba(106,143,170,.7)"; ctx.font = "9px 'Share Tech Mono'";
      ctx.fillText((v / 1000).toFixed(1) + "k", 2, pad.t + (ch / 4) * i + 3);
    });
  }, []);

  return (
    <div>
      <canvas ref={canvasRef} style={{ width: "100%", display: "block" }} height={100} />
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4, fontFamily: F.mono, fontSize: 9, color: C.textD }}>
        {PROD_LABELS.map(l => <span key={l}>{l}</span>)}
      </div>
    </div>
  );
}

// ── Mine Map ──
function MineMap() {
  const [trucks, setTrucks] = useState([
    { id: "t1", l: 45, t: 30 }, { id: "t2", l: 55, t: 45 },
    { id: "t3", l: 35, t: 55 }, { id: "t4", l: 60, t: 60 }
  ]);
  const paths = [
    [[45,30],[40,22],[40,40],[22,60],[45,30]],
    [[55,45],[65,35],[40,22],[40,50],[55,45]],
    [[35,55],[22,60],[40,55],[65,35],[35,55]],
    [[60,60],[78,70],[65,35],[40,55],[60,60]],
  ];
  const stepRef = useRef(0);
  useEffect(() => {
    const iv = setInterval(() => {
      stepRef.current++;
      setTrucks(prev => prev.map((tr, i) => {
        const path = paths[i];
        const pos = path[stepRef.current % path.length];
        return { ...tr, l: pos[0], t: pos[1] };
      }));
    }, 2800);
    return () => clearInterval(iv);
  }, []);

  const nodes = [
    { l: 40, t: 22, icon: "🏗", label: "PALA-01", col: C.accent },
    { l: 65, t: 35, icon: "🏗", label: "PALA-03", col: C.accent },
    { l: 22, t: 60, icon: "🏭", label: "PLANTA", col: C.green },
    { l: 78, t: 70, icon: "⛽", label: "SURTIDOR", col: C.gold },
  ];

  return (
    <div style={{ position: "relative", height: 190, background: "#08111a", borderRadius: 3, overflow: "hidden" }}>
      {/* Grid */}
      <div style={{
        position: "absolute", inset: 0,
        backgroundImage: "linear-gradient(rgba(0,200,255,.04) 1px,transparent 1px),linear-gradient(90deg,rgba(0,200,255,.04) 1px,transparent 1px)",
        backgroundSize: "30px 30px"
      }} />
      {/* Roads */}
      {[
        { left:"20%",top:"30%",width:"60%",height:6,transform:"rotate(-8deg)" },
        { left:"15%",top:"55%",width:"70%",height:6,transform:"rotate(5deg)" },
        { left:"40%",top:"20%",width:6,height:"65%" },
      ].map((r,i) => (
        <div key={i} style={{ position:"absolute", background:"rgba(0,200,255,.12)", borderRadius:3, ...r }} />
      ))}
      {/* Nodes */}
      {nodes.map((n, i) => (
        <div key={i} style={{ position:"absolute", left:`${n.l}%`, top:`${n.t}%`, transform:"translate(-50%,-50%)" }}>
          <div style={{
            width:28, height:28, background:`${n.col}15`, border:`2px solid ${n.col}`,
            borderRadius:4, display:"flex", alignItems:"center", justifyContent:"center",
            fontSize:13, cursor:"pointer"
          }}>{n.icon}</div>
          <div style={{ position:"absolute", bottom:"100%", left:"50%", transform:"translateX(-50%)", fontFamily:F.mono, fontSize:8, color:C.textS, whiteSpace:"nowrap", paddingBottom:2 }}>{n.label}</div>
        </div>
      ))}
      {/* Trucks */}
      {trucks.map(tr => (
        <div key={tr.id} className="truck-dot" style={{
          position:"absolute", left:`${tr.l}%`, top:`${tr.t}%`,
          width:8, height:8, borderRadius:"50%", background:C.gold,
          boxShadow:`0 0 6px ${C.gold}`, transform:"translate(-50%,-50%)",
          transition:"left 2.6s ease-in-out, top 2.6s ease-in-out"
        }} />
      ))}
      {/* Legend */}
      <div style={{ position:"absolute", bottom:6, left:8, display:"flex", gap:10, fontFamily:F.mono, fontSize:8, color:C.textD }}>
        <span>🟡 Camiones</span><span>🔵 Palas</span><span>🟢 Planta</span>
      </div>
    </div>
  );
}

// ── Main Component ──
export default function PIOM() {
  const [activeNav, setActiveNav] = useState("Dashboard");
  const [clock, setClock] = useState("");
  const [syncSec, setSyncSec] = useState(0);
  const [prodVal, setProdVal] = useState(47820);
  const [cicloVal, setCicloVal] = useState(38.4);
  const [messages, setMessages] = useState([
    { role: "ai", text: "¡Hola! Soy el asistente inteligente de PIOM. Monitoreo la operación en tiempo real.\n\nActualmente detecto 2 alertas críticas que requieren atención. ¿Deseas que te explique qué está ocurriendo?", time: "07:02" }
  ]);
  const [inputVal, setInputVal] = useState("");
  const [typing, setTyping] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    const iv = setInterval(() => {
      const now = new Date();
      setClock(now.toTimeString().slice(0, 8));
    }, 1000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const iv = setInterval(() => setSyncSec(s => s >= 30 ? 0 : s + 1), 1000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    const iv = setInterval(() => {
      setProdVal(47820 + Math.floor((Math.random() - .5) * 200));
      setCicloVal(+(38.4 + (Math.random() - .5) * .4).toFixed(1));
    }, 8000);
    return () => clearInterval(iv);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const sendMsg = (q) => {
    const msg = q || inputVal.trim();
    if (!msg) return;
    setInputVal("");
    const now = new Date().toTimeString().slice(0, 5);
    setMessages(prev => [...prev, { role: "user", text: msg, time: now }]);
    setTyping(true);
    setTimeout(() => {
      setTyping(false);
      const resp = AI_RESPONSES[msg];
      const aiTime = new Date().toTimeString().slice(0, 5);
      setMessages(prev => [...prev, {
        role: "ai",
        text: resp ? resp.text : "Analizando datos operacionales... No encontré respuesta específica para esa consulta. ¿Puedes especificar un equipo, sector o indicador?",
        data: resp?.data,
        time: aiTime
      }]);
    }, 1200 + Math.random() * 600);
  };

  const navItems = ["Dashboard","Despacho","Equipos","Planificación","Reportes"];
  const sideItems = [
    { label:"Visión General", ico:"◈", active:true },
    { label:"Mapa Operacional", ico:"⬡" },
    { label:"Ciclos Carguío", ico:"▦", badge:"OK", badgeOk:true },
    { label:"Ciclos Transporte", ico:"⟳" },
  ];
  const sideItems2 = [
    { label:"Camiones (18)", ico:"🚛", badge:"16", badgeOk:true },
    { label:"Palas (6)", ico:"🏗", badge:"5", badgeOk:true },
    { label:"Mantenimiento", ico:"🔧", badge:"3" },
  ];
  const sideItems3 = [
    { label:"KPIs Turno", ico:"📊" },
    { label:"Alertas (4)", ico:"⚠", badge:"4" },
    { label:"Tendencias", ico:"📈" },
    { label:"Predicciones IA", ico:"🔮" },
  ];

  const pf = (pct) => pct>=90 ? C.green : pct>=70 ? C.accent : pct>=50 ? C.warn : C.danger;

  const alerts = [
    { icon:"🔴", title:"Cuello de botella · Sector B — Cola >8 camiones en espera", badge:"CRÍTICO", badgeC:C.danger, badgeBg:"rgba(255,61,90,.15)", time:"Detectado 14:23 · Duración 12 min" },
    { icon:"🔴", title:"CA-12 · Ciclo extendido 52 min (+48% sobre objetivo)", badge:"CRÍTICO", badgeC:C.danger, badgeBg:"rgba(255,61,90,.15)", time:"Detectado 14:31 · Posible falla mecánica" },
    { icon:"🟡", title:"Producción acumulada 8% bajo meta proyectada", badge:"ALERTA", badgeC:C.warn, badgeBg:"rgba(255,159,28,.12)", time:"Actualizado 14:35 · Tendencia negativa" },
    { icon:"🔵", title:"PALA-04 · Rendimiento 12% bajo histórico del equipo", badge:"INFO", badgeC:C.accent, badgeBg:"rgba(0,200,255,.1)", time:"Detectado 13:58 · Monitorear 30 min" },
  ];

  const trucks18 = Array.from({length:18},(_,i)=>({id:`CA-${String(i+1).padStart(2,"0")}`,st:i<16?"op":i===16?"idle":"maint"}));
  const quickQueries = ["¿Por qué bajó la producción?","¿Qué equipo genera más retraso?","Mejor asignación de camiones","¿Qué acción tomar ahora?"];

  return (
    <div style={{ fontFamily:F.body, background:C.bg, color:C.text, height:"100vh", display:"flex", flexDirection:"column", overflow:"hidden" }}>
      <style>{css}</style>

      {/* TOPBAR */}
      <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"0 18px", height:50, background:"#080d14", borderBottom:`1px solid ${C.border}`, flexShrink:0, position:"relative" }}>
        <div style={{ position:"absolute", bottom:0, left:0, right:0, height:1, background:"linear-gradient(90deg,transparent,rgba(0,200,255,.4),transparent)" }} />
        <div style={{ display:"flex", alignItems:"center", gap:10 }}>
          <div className="pulse" style={{ width:30, height:30, background:"linear-gradient(135deg,#00c8ff,#0055aa)", clipPath:"polygon(50% 0%,100% 25%,100% 75%,50% 100%,0% 75%,0% 25%)", display:"flex", alignItems:"center", justifyContent:"center" }}>⬡</div>
          <div>
            <div style={{ fontFamily:F.title, fontSize:20, fontWeight:700, letterSpacing:3, color:C.accent }}>PIOM</div>
            <div style={{ fontSize:9, color:C.textS, letterSpacing:1.5 }}>FAENA NORTE GRANDE · TURNO A</div>
          </div>
        </div>
        <div style={{ display:"flex", gap:4 }}>
          {navItems.map(n => (
            <button key={n} className={`nav-btn${activeNav===n?" active":""}`} onClick={()=>setActiveNav(n)}
              style={{ padding:"5px 14px", background:"transparent", border:"1px solid transparent", borderRadius:3, color:C.textS, fontFamily:F.title, fontSize:12, fontWeight:600, letterSpacing:1.5, textTransform:"uppercase" }}>
              {n}
            </button>
          ))}
        </div>
        <div style={{ display:"flex", alignItems:"center", gap:14 }}>
          <div style={{ display:"flex", alignItems:"center", gap:6, fontFamily:F.mono, fontSize:11, color:C.green }}>
            <div className="blink" style={{ width:7, height:7, borderRadius:"50%", background:C.green }} /> EN VIVO
          </div>
          <div style={{ padding:"2px 10px", background:"rgba(240,165,0,.1)", border:`1px solid ${C.gold}`, borderRadius:3, fontSize:10, fontWeight:600, color:C.gold, letterSpacing:1 }}>TURNO A · 07:00–19:00</div>
          <div style={{ fontFamily:F.mono, fontSize:13, color:C.accent, letterSpacing:2 }}>{clock}</div>
        </div>
      </div>

      {/* MAIN */}
      <div style={{ display:"grid", gridTemplateColumns:"190px 1fr 290px", flex:1, overflow:"hidden" }}>

        {/* SIDEBAR */}
        <div style={{ background:C.panel, borderRight:`1px solid ${C.border}`, display:"flex", flexDirection:"column", overflowY:"auto", padding:"10px 0" }}>
          {[{label:"Estado Faena",items:sideItems},{label:"Equipos",items:sideItems2},{label:"Análisis",items:sideItems3}].map(section => (
            <div key={section.label}>
              <div style={{ padding:"8px 14px 3px", fontSize:9, fontWeight:700, letterSpacing:2, color:C.textD, textTransform:"uppercase", marginTop:6 }}>{section.label}</div>
              {section.items.map(item => (
                <div key={item.label} className={`sidebar-item${item.active?" active":""}`} style={{ display:"flex", alignItems:"center", gap:8, padding:"7px 14px", color:C.textS, fontSize:12, fontWeight:500 }}>
                  <span style={{ fontSize:14, width:16, textAlign:"center" }}>{item.ico}</span>
                  <span style={{ flex:1 }}>{item.label}</span>
                  {item.badge && <span style={{ padding:"1px 5px", borderRadius:10, fontSize:9, fontFamily:F.mono, background:item.badgeOk?"rgba(0,232,122,.15)":"rgba(255,61,90,.15)", color:item.badgeOk?C.green:C.danger }}>{item.badge}</span>}
                </div>
              ))}
            </div>
          ))}
          <div style={{ marginTop:8, padding:"8px 14px 3px", fontSize:9, fontWeight:700, letterSpacing:2, color:C.textD, textTransform:"uppercase" }}>Sistema</div>
          {[{ico:"⚙",label:"Configuración"},{ico:"📡",label:"Integraciones"},{ico:"👤",label:"J. Muñoz · Desp."}].map(i=>(
            <div key={i.label} className="sidebar-item" style={{ display:"flex", alignItems:"center", gap:8, padding:"7px 14px", color:C.textS, fontSize:12 }}>
              <span style={{ fontSize:14 }}>{i.ico}</span><span>{i.label}</span>
            </div>
          ))}
        </div>

        {/* CONTENT */}
        <div style={{ overflowY:"auto", padding:12, display:"flex", flexDirection:"column", gap:10 }}>

          {/* KPIs */}
          <div style={{ display:"flex", gap:8 }}>
            <KpiCard label="Producción Turno" value={prodVal.toLocaleString("es-CL")} unit="ton · meta: 52,000" delta="3.2% vs turno ant." deltaUp={false} color={C.accent} topColor={C.accent} sparkData={[82,91,98,86,90,78,88,92,85]} />
            <KpiCard label="Ciclo Promedio" value={cicloVal} unit="min · objetivo: ≤35" delta="Sobre objetivo" deltaUp={false} color={C.gold} topColor={C.gold} sparkData={[35,36,34,37,38,36,39,38,38]} />
            <KpiCard label="Disponibilidad Flota" value="88.9%" unit="16/18 camiones activos" delta="+1.2% vs ayer" deltaUp={true} color={C.green} topColor={C.green} sparkData={[92,90,88,91,89,90,88,89,89]} />
            <KpiCard label="Alertas Activas" value="4" unit="2 críticas · 2 alertas" delta="Requiere acción" deltaUp={false} color={C.danger} topColor={C.danger} sparkData={[1,2,1,3,2,4,3,4,4]} />
            <KpiCard label="Eficiencia PIOM IA" value="92.4%" unit="Índice PIOM Score" delta="Operación estable" deltaUp={true} color={C.purple} topColor={C.purple} sparkData={[88,91,93,90,92,89,94,91,92]} />
          </div>

          {/* ROW 2 */}
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>

            {/* Fleet */}
            <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:4, overflow:"hidden" }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"9px 14px", borderBottom:`1px solid ${C.border}`, background:C.panel }}>
                <div style={{ fontFamily:F.title, fontSize:13, fontWeight:600, letterSpacing:1, textTransform:"uppercase" }}>Estado de Flota</div>
                <div style={{ padding:"2px 7px", background:"rgba(0,232,122,.12)", border:`1px solid rgba(0,232,122,.3)`, borderRadius:2, fontSize:9, fontFamily:F.mono, color:C.green }}>● EN VIVO</div>
              </div>
              <div style={{ padding:"10px 12px" }}>
                <div style={{ display:"flex", gap:16, marginBottom:8 }}>
                  {[{c:C.green,l:"Operativo (16)"},{c:C.gold,l:"Espera (1)"},{c:C.danger,l:"Mant. (1)"}].map(x=>(
                    <div key={x.l} style={{ display:"flex", alignItems:"center", gap:5, fontSize:10 }}>
                      <div style={{ width:7,height:7,borderRadius:"50%",background:x.c }} /><span style={{ color:x.c }}>{x.l}</span>
                    </div>
                  ))}
                </div>
                <div style={{ display:"grid", gridTemplateColumns:"repeat(6,1fr)", gap:4 }}>
                  {trucks18.map(tr=>(
                    <div key={tr.id} className="fleet-cell" style={{
                      aspectRatio:1, borderRadius:3, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center",
                      gap:1, fontFamily:F.mono, fontSize:8, border:"1px solid",
                      background:tr.st==="op"?"rgba(0,232,122,.08)":tr.st==="idle"?"rgba(240,165,0,.08)":"rgba(255,61,90,.08)",
                      borderColor:tr.st==="op"?"rgba(0,232,122,.3)":tr.st==="idle"?"rgba(240,165,0,.3)":"rgba(255,61,90,.3)",
                      color:tr.st==="op"?C.green:tr.st==="idle"?C.gold:C.danger
                    }}>
                      <div style={{ fontSize:13 }}>🚛</div>
                      <div>{tr.id}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Map */}
            <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:4, overflow:"hidden" }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"9px 14px", borderBottom:`1px solid ${C.border}`, background:C.panel }}>
                <div style={{ fontFamily:F.title, fontSize:13, fontWeight:600, letterSpacing:1, textTransform:"uppercase" }}>Mapa Operacional</div>
                <div style={{ padding:"2px 7px", background:"rgba(0,232,122,.12)", border:`1px solid rgba(0,232,122,.3)`, borderRadius:2, fontSize:9, fontFamily:F.mono, color:C.green }}>● TIEMPO REAL</div>
              </div>
              <div style={{ padding:8 }}><MineMap /></div>
            </div>
          </div>

          {/* ROW 3 */}
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:10 }}>

            {/* Equipment Table */}
            <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:4, overflow:"hidden" }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"9px 14px", borderBottom:`1px solid ${C.border}`, background:C.panel }}>
                <div style={{ fontFamily:F.title, fontSize:13, fontWeight:600, letterSpacing:1, textTransform:"uppercase" }}>Rendimiento Equipos</div>
                <div style={{ padding:"2px 7px", background:"rgba(255,159,28,.12)", border:`1px solid rgba(255,159,28,.3)`, borderRadius:2, fontSize:9, fontFamily:F.mono, color:C.warn }}>⚠ 1 ALERTA</div>
              </div>
              <table style={{ width:"100%", borderCollapse:"collapse" }}>
                <thead>
                  <tr>{["Equipo","Estado","Sector","Ciclos/Hr","Carga %","Ton/Hr"].map(h=>(
                    <th key={h} style={{ fontSize:9, letterSpacing:"1.2px", textTransform:"uppercase", color:C.textD, padding:"5px 10px", textAlign:"left", borderBottom:`1px solid ${C.border}`, fontFamily:F.body }}>{h}</th>
                  ))}</tr>
                </thead>
                <tbody>
                  {EQUIP.map(e=>{
                    const isWarn = e.id==="PALA-04", isMaint=e.st==="maint";
                    return (
                      <tr key={e.id} className="eq-row" style={{ background:isWarn?"rgba(255,159,28,.03)":"transparent" }}>
                        <td style={{ padding:"7px 10px", fontSize:11, fontFamily:F.mono, color:C.accent }}>{e.id}{isWarn?" ⚠":""}</td>
                        <td style={{ padding:"7px 10px" }}>
                          <div style={{ display:"flex", alignItems:"center", gap:5, fontSize:11 }}>
                            <div style={{ width:6,height:6,borderRadius:"50%",background:isMaint?C.danger:C.green }} />
                            <span style={{ color:isMaint?C.danger:C.green }}>{isMaint?"Mantención":"Operativo"}</span>
                          </div>
                        </td>
                        <td style={{ padding:"7px 10px" }}>
                          {e.sector!=="—"&&<span style={{ padding:"1px 5px", borderRadius:2, fontSize:10, fontFamily:F.mono, background:e.sector==="A"?"rgba(0,200,255,.1)":e.sector==="B"?"rgba(240,165,0,.1)":"rgba(168,85,247,.1)", color:e.sector==="A"?C.accent:e.sector==="B"?C.gold:C.purple }}>{e.sector}</span>}
                          {e.sector==="—"&&<span style={{color:C.textD}}>—</span>}
                        </td>
                        <td style={{ padding:"7px 10px", fontFamily:F.mono, fontSize:11, color:isWarn?C.warn:C.text }}>{e.ciclos||"—"}</td>
                        <td style={{ padding:"7px 10px" }}>
                          <div style={{ display:"flex", alignItems:"center", gap:5 }}>
                            <div style={{ width:52, height:5, background:C.border, borderRadius:3, overflow:"hidden" }}>
                              <div style={{ height:"100%", borderRadius:3, width:`${e.carga}%`, background:pf(e.carga), transition:"width 1s" }} />
                            </div>
                            <span style={{ fontFamily:F.mono, fontSize:10, color:C.textS }}>{e.carga||0}%</span>
                          </div>
                        </td>
                        <td style={{ padding:"7px 10px", fontFamily:F.mono, fontSize:11, color:C.accent }}>{e.tonhr||"—"}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Alerts */}
            <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:4, overflow:"hidden" }}>
              <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"9px 14px", borderBottom:`1px solid ${C.border}`, background:C.panel }}>
                <div style={{ fontFamily:F.title, fontSize:13, fontWeight:600, letterSpacing:1, textTransform:"uppercase" }}>Alertas Operacionales</div>
                <div style={{ padding:"2px 7px", background:"rgba(255,159,28,.12)", border:`1px solid rgba(255,159,28,.3)`, borderRadius:2, fontSize:9, fontFamily:F.mono, color:C.warn }}>4 ACTIVAS</div>
              </div>
              <div style={{ padding:"10px 14px" }}>
                {alerts.map((a,i)=>(
                  <div key={i} style={{ display:"flex", gap:8, padding:"8px 0", borderBottom:i<alerts.length-1?`1px solid rgba(26,42,58,.6)`:"none" }}>
                    <div style={{ fontSize:14, flexShrink:0, marginTop:1 }}>{a.icon}</div>
                    <div>
                      <div style={{ fontSize:12, color:C.text, marginBottom:3, fontWeight:500 }}>{a.title}</div>
                      <span style={{ padding:"2px 6px", borderRadius:2, fontSize:9, fontWeight:700, letterSpacing:1, background:a.badgeBg, color:a.badgeC, border:`1px solid ${a.badgeC}33` }}>{a.badge}</span>
                      <div style={{ fontFamily:F.mono, fontSize:9, color:C.textD, marginTop:3 }}>{a.time}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Production Chart */}
          <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:4, overflow:"hidden" }}>
            <div style={{ display:"flex", alignItems:"center", justifyContent:"space-between", padding:"9px 14px", borderBottom:`1px solid ${C.border}`, background:C.panel }}>
              <div style={{ fontFamily:F.title, fontSize:13, fontWeight:600, letterSpacing:1, textTransform:"uppercase" }}>Producción por Hora — Turno Actual</div>
              <div style={{ display:"flex", gap:8, alignItems:"center" }}>
                <div style={{ fontFamily:F.mono, fontSize:10, color:C.textD }}>Meta/hr: 5,200 ton</div>
                <div style={{ padding:"2px 7px", background:"rgba(0,232,122,.12)", border:`1px solid rgba(0,232,122,.3)`, borderRadius:2, fontSize:9, fontFamily:F.mono, color:C.green }}>● EN VIVO</div>
              </div>
            </div>
            <div style={{ padding:"10px 14px" }}><ProdChart /></div>
          </div>

        </div>{/* /content */}

        {/* RIGHT PANEL: AI CHAT */}
        <div style={{ background:C.panel, borderLeft:`1px solid ${C.border}`, display:"flex", flexDirection:"column", overflow:"hidden" }}>
          {/* Chat header */}
          <div style={{ padding:"12px 14px", borderBottom:`1px solid ${C.border}`, display:"flex", alignItems:"center", gap:10, flexShrink:0 }}>
            <div style={{ width:34, height:34, background:"linear-gradient(135deg,#003366,#00c8ff)", borderRadius:7, display:"flex", alignItems:"center", justifyContent:"center", fontSize:16, boxShadow:"0 0 14px rgba(0,200,255,.25)", flexShrink:0 }}>🤖</div>
            <div>
              <div style={{ fontFamily:F.title, fontSize:14, fontWeight:700, letterSpacing:1 }}>Asistente PIOM IA</div>
              <div style={{ fontSize:10, color:C.green, fontFamily:F.mono }}>● Conectado · Modelo v2.4</div>
            </div>
          </div>

          {/* Messages */}
          <div style={{ flex:1, overflowY:"auto", padding:10, display:"flex", flexDirection:"column", gap:8 }}>
            {messages.map((m,i)=>(
              <div key={i} className="msg-in" style={{ display:"flex", flexDirection:"column", maxWidth:"92%", alignSelf:m.role==="user"?"flex-end":"flex-start", alignItems:m.role==="user"?"flex-end":"flex-start" }}>
                <div style={{
                  padding:"8px 11px", borderRadius:6, fontSize:12, lineHeight:1.55,
                  background:m.role==="user"?"rgba(0,200,255,.09)":C.card,
                  border:m.role==="user"?`1px solid rgba(0,200,255,.2)`:`1px solid ${C.border}`,
                  borderBottomRightRadius:m.role==="user"?2:6,
                  borderBottomLeftRadius:m.role==="ai"?2:6,
                  whiteSpace:"pre-line"
                }}>{m.text}</div>
                {m.data && (
                  <div style={{ marginTop:5, padding:"6px 10px", background:"rgba(0,200,255,.04)", border:`1px solid rgba(0,200,255,.12)`, borderRadius:4, fontFamily:F.mono, fontSize:10, color:C.textS, width:"100%" }}>
                    {m.data.map((d,j)=>(
                      <div key={j} style={{ display:"flex", justifyContent:"space-between", padding:"2px 0" }}>
                        <span>{d.k}</span><span style={{ color:C.accent }}>{d.v}</span>
                      </div>
                    ))}
                  </div>
                )}
                <div style={{ fontFamily:F.mono, fontSize:9, color:C.textD, marginTop:3, padding:"0 2px" }}>{m.time} — {m.role==="user"?"Tú":"PIOM IA"}</div>
              </div>
            ))}
            {typing && (
              <div style={{ alignSelf:"flex-start" }}>
                <div style={{ padding:"10px 14px", background:C.card, border:`1px solid ${C.border}`, borderRadius:6, display:"flex", gap:4 }}>
                  {[0,.2,.4].map(d=>(
                    <div key={d} style={{ width:6,height:6,borderRadius:"50%",background:C.accent,animation:`blink 1.2s ${d}s infinite` }} />
                  ))}
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Quick queries */}
          <div style={{ padding:"8px 10px", borderTop:`1px solid ${C.border}`, flexShrink:0 }}>
            <div style={{ fontSize:9, letterSpacing:1, color:C.textD, textTransform:"uppercase", marginBottom:4, fontFamily:F.body }}>Consultas rápidas</div>
            {quickQueries.map(q=>(
              <button key={q} className="quick-btn" onClick={()=>sendMsg(q)} style={{
                display:"block", width:"100%", marginBottom:3, padding:"5px 9px",
                background:C.card, border:`1px solid ${C.border}`, borderRadius:3,
                color:C.textS, fontSize:11, fontFamily:F.body
              }}>⚡ {q}</button>
            ))}
          </div>

          {/* Input */}
          <div style={{ display:"flex", gap:6, padding:"9px 10px", borderTop:`1px solid ${C.border}`, flexShrink:0 }}>
            <input
              value={inputVal}
              onChange={e=>setInputVal(e.target.value)}
              onKeyDown={e=>e.key==="Enter"&&sendMsg()}
              placeholder="Consulta en lenguaje natural..."
              style={{ flex:1, background:C.card, border:`1px solid ${C.border}`, borderRadius:4, padding:"7px 10px", color:C.text, fontFamily:F.body, fontSize:12, outline:"none" }}
            />
            <button className="send-btn" onClick={()=>sendMsg()} style={{ padding:"7px 13px", background:C.accent, color:"#000", border:"none", borderRadius:4, fontWeight:700, fontSize:11, fontFamily:F.title, letterSpacing:1 }}>
              ENVIAR
            </button>
          </div>
        </div>
      </div>

      {/* STATUS BAR */}
      <div style={{ height:22, background:"#050810", borderTop:`1px solid ${C.border}`, display:"flex", alignItems:"center", gap:18, padding:"0 14px", flexShrink:0, fontFamily:F.mono, fontSize:9, color:C.textD }}>
        {[{label:"FMS Conectado"},{label:"IoT · 134 sensores"},{label:"ERP Integrado"}].map(x=>(
          <div key={x.label} style={{ display:"flex", alignItems:"center", gap:4 }}>
            <div style={{ width:5,height:5,borderRadius:"50%",background:C.green }} />
            <span style={{ color:C.textS }}>{x.label}</span>
          </div>
        ))}
        <span style={{ color:C.textS }}>Última sync: <span style={{ color:C.textS }}>hace {syncSec}s</span></span>
        <span style={{ marginLeft:"auto", color:C.gold }}>⚠ 4 alertas activas</span>
        <span>PIOM v2.4.1 · Anthropic AI Engine</span>
      </div>
    </div>
  );
}
