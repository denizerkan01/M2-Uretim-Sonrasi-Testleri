from __future__ import annotations
import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
PORT = 8782
TESTS = [
    ("01", "Data Select Kontrol Testi"),
    ("02", "Kalibrasyon Kontrol Testi"),
    ("03", "Reset Testi"),
    ("04", "Acc Norm ve Gyro Açılış Testi"),
    ("05", "Acc Döndürme Testi"),
    ("06", "Euler Kontrol Testi"),
    ("07", "Gyro Z Testi"),
    ("08", "Bağlantı Testi (RS422 / RS232)"),
]
lock = threading.RLock()
state = {"running": False, "pn": "", "sn": "", "device": {"pn_dvc": "—", "sn_dvc": "—", "pn_match": None, "sn_match": None, "connection": None, "standard_com": "—", "enhanced_com": "—"}, "information": [], "tests": {n: {"status": "Bekliyor", "result": None} for n, _ in TESTS}, "logs": [], "error": None, "started_at": None, "box_rotation": 0, "box_rotation_y": 0, "box_motion_id": 0, "box_motion": []}
process = None


def add_log(line: str):
    global state
    line = line.rstrip()
    if not line:
        return
    lowered_line = line.casefold()
    rotation_motions = {
        "sistemi 2. konuma getirin": [{"x": 90, "y": 0, "axis": "x", "direction": 1}],
        "sistemi 3. konuma getirin": [{"x": 180, "y": 0, "axis": "x", "direction": 1}],
        "sistemi 4. konuma getirin": [{"x": 270, "y": 0, "axis": "x", "direction": 1}],
        "sistemi 5. konuma getirin": [
            {"x": 360, "y": 0, "axis": "x", "direction": 1},
            {"x": 360, "y": 90, "axis": "y", "direction": 1, "style": "externalLeft"},
        ],
        "sistemi 6. konuma getirin": [{"x": 360, "y": -90, "axis": "y", "direction": -1}],
    }
    rotation_motion = next((motion for phrase, motion in rotation_motions.items() if phrase in lowered_line), None)
    with lock:
        if rotation_motion is not None:
            state["box_motion_id"] += 1
            state["box_motion"] = rotation_motion
            state["box_rotation"] = rotation_motion[-1]["x"]
            state["box_rotation_y"] = rotation_motion[-1]["y"]
        state["logs"].append({"time": time.strftime("%H:%M:%S"), "text": line})
        state["logs"] = state["logs"][-250:]
        if line.startswith("***Test "):
            try:
                number = line.split("***Test ", 1)[1].split(":", 1)[0].zfill(2)
                if number in state["tests"]:
                    state["tests"][number]["status"] = "Çalışıyor"
            except Exception:
                pass
        if "TAMAMLANDI" in line:
            try:
                number = line.split("***Test ", 1)[1].split(":", 1)[0].zfill(2)
                if number in state["tests"]:
                    state["tests"][number]["status"] = "Tamamlandı"
            except Exception:
                pass
        if line.startswith("GUI_RESULT|"):
            parts = line.split("|", 2)
            if len(parts) == 3 and parts[1] in state["tests"]:
                state["tests"][parts[1]]["result"] = parts[2].strip().lower() == "true"
        if line.startswith("GUI_DEVICE|") or line.startswith("GUI_PORT|") or line.startswith("GUI_CONNECTION|"):
            parts = line.split("|", 2)
            if line.startswith("GUI_CONNECTION|"):
                state["device"]["connection"] = line.split("|", 1)[1].strip().lower() == "true"
            elif len(parts) == 3:
                key_map = {"pn_dvc": "pn_dvc", "sn_dvc": "sn_dvc", "pn_match": "pn_match", "sn_match": "sn_match", "standard": "standard_com", "enhanced": "enhanced_com"}
                key = key_map.get(parts[1])
                if key:
                    value = parts[2].strip()
                    state["device"][key] = value.lower() == "true" if key.endswith("_match") else (value or "Bulunamadı")
        if line.startswith("GUI_INFO|"):
            parts = line.split("|", 2)
            messages = {"firmware_version_match": "FW Eşleşmedi Sistemde yanlış FW bulunmaktadır.", "acc_is_calibrated": "Sistemde Acc kalibrasyonu bulunmamaktadır. Test yapılamaz", "gyro_is_calibrated": "Sistemde Gyro kalibrasyonu bulunmamaktadır. Test yapılamaz"}
            if len(parts) == 3 and parts[1] in messages and parts[2].strip().lower() == "false":
                message = messages[parts[1]]
                if message not in state["information"]:
                    state["information"].append(message)


def monitor(proc):
    global process
    try:
        for line in iter(proc.stdout.readline, ""):
            add_log(line)
        code = proc.wait()
        with lock:
            state["running"] = False
            if code:
                state["error"] = f"Python işlemi kod {code} ile sonlandı."
                add_log(state["error"])
            else:
                add_log("Test akışı tamamlandı.")
    except Exception as exc:
        with lock:
            state["running"] = False
            state["error"] = str(exc)
            add_log(f"Backend hata: {exc}")
    finally:
        process = None


PAGE = r'''<!doctype html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>M2GR Üretim Testi</title><style>
:root{font-family:Inter,"Segoe UI",Arial,sans-serif;color:#172033;background:#f3f6fb}*{box-sizing:border-box}body{margin:0}.top{height:78px;background:#fff;border-bottom:1px solid #e4e9f1;padding:14px 24px;display:flex;align-items:center;justify-content:space-between}.brand{font-size:20px;font-weight:700}.muted{color:#718096;font-size:13px;margin-top:4px}.badge{border-radius:20px;background:#edf2f7;color:#586174;padding:8px 14px;font-size:13px}.badge.on{background:#e3f7ee;color:#158456}.wrap{width:100%;max-width:none;margin:0;padding:14px 18px 18px;display:grid;grid-template-columns:minmax(290px,.82fr) minmax(520px,1.35fr) minmax(340px,.95fr);grid-template-rows:minmax(250px,.82fr) minmax(340px,1.18fr);gap:14px;height:calc(100vh - 78px);min-height:720px;overflow:auto}.card{background:#fff;border:1px solid #e5eaf1;border-radius:14px;padding:18px;box-shadow:0 4px 16px #1a2b4608;margin:0;min-width:0;min-height:0}.section-title{font-size:18px;font-weight:650;margin:0 0 14px}.start-card{grid-column:1;grid-row:1}.device-card{grid-column:1;grid-row:2;overflow:auto}.fields{display:grid;grid-template-columns:1fr;gap:10px;align-items:end}label{display:block;color:#738096;font-size:11px;margin:0 0 6px}input{width:100%;border:1px solid #dce3ed;border-radius:9px;padding:10px 11px;font:inherit;font-size:13px;outline:0}input:focus{border-color:#6485f5}button{border:0;border-radius:9px;padding:10px 16px;font:inherit;font-weight:600;font-size:13px;cursor:pointer}.start{background:#315de8;color:#fff}.stop{background:#fff1f0;color:#c63b34;border:1px solid #f6d4d1;margin-left:8px}.buttons{display:flex;white-space:nowrap}.buttons button{flex:1}.hint{font-size:10px;line-height:1.45;color:#77849a;margin-top:10px}.device-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.device-item{min-height:76px;border:1px solid #e8edf4;border-radius:10px;padding:9px;display:flex;flex-direction:column;align-items:flex-start;gap:5px}.device-item strong{font-size:12px;word-break:break-word}.device-item small{font-size:10px;color:#738096}.tag{display:inline-block;padding:4px 7px;border-radius:7px;background:#f1f4f8;color:#758195;font-size:10px;font-weight:650}.tag.pass{background:#e2f7ed;color:#178555}.tag.fail{background:#fde8e6;color:#c53d35}.flow-card{grid-column:2;grid-row:1 / span 2;display:flex;flex-direction:column;overflow:hidden}.grid{display:grid;grid-template-columns:1fr;gap:7px;overflow:auto;min-height:0}.test{display:flex;align-items:center;gap:9px;border:1px solid #e8edf4;border-radius:9px;padding:8px 9px;min-height:38px}.num{font-weight:700;color:#6a7b98;background:#f0f3f8;border-radius:7px;padding:5px 6px;font-size:10px}.name{flex:1;font-size:11px}.status{font-size:10px;color:#738096}.result{font-size:10px;font-weight:700;padding:4px 8px;border-radius:7px;background:#f1f4f8;color:#7d8797;min-width:50px;text-align:center}.result.pass{background:#e2f7ed;color:#178555}.result.fail{background:#fde8e6;color:#c53d35}.todo-card{grid-column:3;grid-row:1;min-height:0;display:flex;flex-direction:column}.box-stage{display:block;width:100%;height:160px;max-width:360px;align-self:center;flex:none;margin:0 auto;overflow:visible}.box-3d-svg{display:block;width:100%;height:100%;overflow:visible}.orientation-instruction{display:flex;align-items:center;justify-content:center;margin-top:5px;color:#394355;font-size:12px;font-weight:600;line-height:1.35;text-align:center}.orientation-instruction span{max-width:240px}.info-card{grid-column:3;grid-row:2;overflow:auto}.info-list{padding-left:20px;margin:0;color:#344054;font-size:12px;line-height:1.6}.info-list li+li{margin-top:8px}.live-card{margin-top:12px;border-top:1px solid #edf0f5;padding-top:12px;min-height:0;display:flex;flex-direction:column}.live-title{font-size:13px;font-weight:650;margin:0 0 8px}.log{height:190px;max-height:25vh;min-height:100px;overflow:auto;background:#111827;color:#dce4f2;border-radius:10px;padding:10px;font:10px/1.55 Consolas,monospace}.entry{display:flex;gap:10px}.time{color:#8291a8;flex:none}.empty{color:#718096}.footer{display:none}@media(max-width:1120px){.wrap{grid-template-columns:minmax(250px,.8fr) minmax(420px,1.2fr);grid-template-rows:auto auto auto;height:auto;min-height:0;overflow:visible}.start-card{grid-column:1;grid-row:1}.device-card{grid-column:1;grid-row:2}.flow-card{grid-column:2;grid-row:1 / span 2;min-height:680px}.todo-card{grid-column:1 / span 2;grid-row:3;min-height:180px}.info-card{grid-column:1 / span 2;grid-row:4;min-height:130px}}@media(max-width:700px){.top{height:auto}.wrap{display:flex;flex-direction:column;padding:12px}.start-card,.device-card,.flow-card,.todo-card{width:100%}.flow-card{min-height:640px}.device-grid{grid-template-columns:1fr 1fr}}
</style></head><body><header class="top"><div><div class="brand">M2GR Üretim Testi</div><div class="muted">ArView bağlantılı test kontrol paneli</div></div><div id="badge" class="badge">Hazır</div></header><main class="wrap"><section class="card start-card"><h2 class="section-title">Testi başlat</h2><div class="fields"><div><label>Etiketteki Part Number (PN)</label><input id="pn" placeholder="Örn. M2GR051433A" autocomplete="off"></div><div><label>Etiketteki Serial Number (SN)</label><input id="sn" placeholder="Etiketteki seri numarası" autocomplete="off"></div><div class="buttons"><button class="start" id="start" onclick="startRun()">Başlat</button><button class="stop" id="stop" onclick="stopRun()" disabled>Durdur</button></div></div><div class="hint">Cihazı PC’ye bağlayıp ArView’i kapalı bırakın. Bu panel test Python’unu başlatır; cihazdan okunan PN/SN girilen etiket değerleriyle karşılaştırılır.</div></section><section class="card device-card"><h2 class="section-title">Cihaz ve bağlantı</h2><div class="device-grid" id="deviceInfo"></div></section><section class="card flow-card"><h2 class="section-title">Test akışı</h2><div class="grid" id="tests"></div><div class="live-card"><h3 class="live-title">Canlı kayıt</h3><div id="logs" class="log"><span class="empty">Test başladığında Python çıktısı burada görünür.</span></div></div></section><section class="card todo-card"><h2 class="section-title">Yapılacaklar</h2><div class="box-stage"><svg id="boxSvg" class="box-3d-svg" viewBox="0 0 300 180" role="img" aria-label="X, Y ve Z eksenleri gösterilen 3D kutu"><g id="boxScene"></g></svg></div><div class="orientation-instruction"><span>Sistemi gösterilen konuma getirin</span></div></section><section class="card info-card"><h2 class="section-title">Bilgilendirme</h2><ul class="info-list" id="informationList"></ul></section></main><script>
const labels={"01":"Data Select Kontrol Testi","02":"Kalibrasyon Kontrol Testi","03":"Reset Testi","04":"Acc Norm ve Gyro Açılış Testi","05":"Acc Döndürme Testi","06":"Euler Kontrol Testi","07":"Gyro Z Testi","08":"Bağlantı Testi (RS422 / RS232)"};
function esc(x){return String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function drawBox(degrees,yDegrees=0,rotationArrow=null){const scene=document.getElementById("boxScene");if(!scene)return;const a=degrees*Math.PI/180,b=yDegrees*Math.PI/180,co=Math.cos(a),si=Math.sin(a),cy=Math.cos(b),sy=Math.sin(b),bx=[42,-42],by=[70,0],bz=[0,70],byX=[co*by[0]+si*bz[0],co*by[1]+si*bz[1]],bzX=[-si*by[0]+co*bz[0],-si*by[1]+co*bz[1]],vx=[cy*bx[0]+sy*bzX[0],cy*bx[1]+sy*bzX[1]],vy=byX,vz=[-sy*bx[0]+cy*bzX[0],-sy*bx[1]+cy*bzX[1]];const P=(x,y,z)=>[vx[0]*x+vy[0]*y+vz[0]*z,vx[1]*x+vy[1]*y+vz[1]*z];const xBack=[[1,0,0],[1,1,0],[1,1,1],[1,0,1],"#202329"],yBack=[[0,0,1],[1,0,1],[1,1,1],[0,1,1],"#24282e"],zBack=[[0,0,0],[1,0,0],[1,0,1],[0,0,1],"#292d33"],front=[[0,0,0],[0,1,0],[0,1,1],[0,0,1],"#282c32"],sideY=[[0,1,0],[1,1,0],[1,1,1],[0,1,1],"#15181c"],sideZ=[[0,0,0],[1,0,0],[1,1,0],[0,1,0],"#565b63"],topZ=[[0,0,0],[1,0,0],[1,1,0],[0,1,0],"#343941"],topY=[[0,0,0],[1,0,0],[1,0,1],[0,0,1],"#343941"];const faceOrders=[[xBack,yBack,zBack,sideY,front,topZ],[xBack,yBack,sideY,sideZ,front,topY],[xBack,sideY,sideZ,front,zBack,yBack],[xBack,zBack,sideZ,front,yBack,sideY]],faceStep=(Math.floor((((degrees%360)+360)%360+45)/90)+Math.floor((((yDegrees%360)+360)%360+45)/90))%4,polys=faceOrders[faceStep];const points=[];for(let x=0;x<=1;x++)for(let y=0;y<=1;y++)for(let z=0;z<=1;z++)points.push(P(x,y,z));const xRoot=P(0,0,0),xTip=P(1.55,0,0),yRoot=P(0,1,0),yTip=P(0,1.62,0),zRoot=P(0,1,1);let zTip=P(0,1,1.62);if(!rotationArrow&&Math.abs(((degrees%360)+360)%360)<.01&&Math.abs(yDegrees-90)<.01){const defaultZTip=P(0,1,1.62);zTip=[2*zRoot[0]-defaultZTip[0],2*zRoot[1]-defaultZTip[1]];}points.push(xRoot,xTip,yRoot,yTip,zRoot,zTip);const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]),ox=150-(Math.min(...xs)+Math.max(...xs))/2,oy=90-(Math.min(...ys)+Math.max(...ys))/2;const fmt=p=>`${(p[0]+ox).toFixed(1)},${(p[1]+oy).toFixed(1)}`;let html=polys.map(f=>`<polygon points="${f.slice(0,4).map(v=>fmt(P(...v))).join(" ")}" fill="${f[4]}" stroke="#101216" stroke-width="2" stroke-linejoin="round"/>`).join("");for(const y of [.34,.68]){const c=P(0,y,.52);html+=`<circle cx="${(c[0]+ox).toFixed(1)}" cy="${(c[1]+oy).toFixed(1)}" r="6.2" fill="#111419" stroke="#a1a7af" stroke-width="1.8"/><circle cx="${(c[0]+ox).toFixed(1)}" cy="${(c[1]+oy).toFixed(1)}" r="2.2" fill="#59616b"/>`;}const axis=(name,r,t,color)=>{const dx=t[0]-r[0],dy=t[1]-r[1],len=Math.hypot(dx,dy)||1,ux=dx/len,uy=dy/len,bx=t[0]-ux*8,by=t[1]-uy*8,px=-uy*3.5,py=ux*3.5,lx=t[0]+ux*8,ly=t[1]+uy*8;return `<line x1="${(r[0]+ox).toFixed(1)}" y1="${(r[1]+oy).toFixed(1)}" x2="${(t[0]+ox).toFixed(1)}" y2="${(t[1]+oy).toFixed(1)}" stroke="${color}" stroke-width="2.7" stroke-linecap="round"/><polygon points="${(t[0]+ox).toFixed(1)},${(t[1]+oy).toFixed(1)} ${(bx+px+ox).toFixed(1)},${(by+py+oy).toFixed(1)} ${(bx-px+ox).toFixed(1)},${(by-py+oy).toFixed(1)}" fill="${color}"/><text x="${(lx+ox).toFixed(1)}" y="${(ly+oy+4).toFixed(1)}" fill="${color}" font-family="Arial,sans-serif" font-size="12" font-weight="700">${name}</text>`;};html+=`<g>${axis("X",xRoot,xTip,"#f59e0b")}${axis("Y",yRoot,yTip,"#8b2eff")}${axis("Z",zRoot,zTip,"#20dc00")}</g>`;if(rotationArrow){const c=P(.5,.5,.5),cx=c[0]+ox,cy=c[1]+oy;if(rotationArrow.style==="externalLeft"){html+=drawExternalLeftArrow(cx,cy);}else if(rotationArrow.style==="frontArc"){html+=drawFrontFaceArrow(P,ox,oy,true);}else{html+=drawRotationArrow(cx,cy,rotationArrow.axis,rotationArrow.direction);}}scene.innerHTML=html;}
function drawRotationArrow(cx,cy,axis,direction){const color=axis==="y"?"#08a889":"#d99c0c",paths={x:[`M${cx+8},${cy-58} C${cx+49},${cy-54} ${cx+63},${cy-18} ${cx+56},${cy+10}`,`M${cx+56},${cy+10} C${cx+63},${cy-18} ${cx+49},${cy-54} ${cx+8},${cy-58}`],y:[`M${cx-8},${cy-58} C${cx-49},${cy-54} ${cx-63},${cy-18} ${cx-56},${cy+10}`,`M${cx-56},${cy+10} C${cx-63},${cy-18} ${cx-49},${cy-54} ${cx-8},${cy-58}`]},d=paths[axis][direction<0?1:0];return `<defs><marker id="rotationArrowHead" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L9,4.5 L0,9 Z" fill="${color}"/></marker></defs><path d="${d}" fill="none" stroke="${color}" stroke-width="3.4" stroke-linecap="round" marker-end="url(#rotationArrowHead)"/>`;}
function drawFrontFaceArrow(P,ox,oy,reverse=false){const p=(y,z)=>P(0,y,z);let curve=[p(-.3,1.15),p(-.6,.8),p(-.6,-.55),p(.55,-.5)];if(reverse)curve=[curve[3],curve[2],curve[1],curve[0]];const fmt=v=>`${(v[0]+ox).toFixed(1)},${(v[1]+oy).toFixed(1)}`;return `<defs><marker id="frontRotationArrowHead" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L12,6 L0,12 Z" fill="#70e000"/></marker></defs><path d="M${fmt(curve[0])} C${fmt(curve[1])} ${fmt(curve[2])} ${fmt(curve[3])}" fill="none" stroke="#70e000" stroke-width="5.2" stroke-linecap="round" marker-end="url(#frontRotationArrowHead)"/>`;}function drawExternalLeftArrow(cx,cy){const color="#f05a24",d=`M${cx-70},${cy+35} C${cx-110},${cy+30} ${cx-115},${cy-40} ${cx-76},${cy-72}`;return `<defs><marker id="externalLeftArrowHead" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L12,6 L0,12 Z" fill="${color}"/></marker></defs><path d="${d}" fill="none" stroke="${color}" stroke-width="4.2" stroke-linecap="round" marker-end="url(#externalLeftArrowHead)"/>`;}let boxAnimationId=0,lastBoxMotionId=null,displayedBoxRotation=0,displayedBoxRotationY=0;
function animateBoxStep(step,runId){return new Promise(resolve=>{const fromX=displayedBoxRotation,fromY=displayedBoxRotationY,start=performance.now(),duration=1050,arrow=step.showArrow===false?null:{axis:step.axis,direction:step.direction,style:step.style};function frame(now){if(runId!==boxAnimationId){resolve();return;}const t=Math.min(1,(now-start)/duration),ease=t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2;displayedBoxRotation=fromX+(step.x-fromX)*ease;displayedBoxRotationY=fromY+(step.y-fromY)*ease;drawBox(displayedBoxRotation,displayedBoxRotationY,t<1?arrow:null);if(t<1)requestAnimationFrame(frame);else{drawBox(step.x,step.y,null);resolve();}}requestAnimationFrame(frame);});}
async function animateBoxMotion(steps){const runId=++boxAnimationId;for(let i=0;i<steps.length;i++){await animateBoxStep(steps[i],runId);if(runId!==boxAnimationId)return;if(i<steps.length-1)await new Promise(resolve=>setTimeout(resolve,180));}}function matchTag(v){return v===true?'<span class="tag pass">Eşleşti</span>':v===false?'<span class="tag fail">Eşleşmedi</span>':'<span class="tag">Bekleniyor</span>'}
function render(s){const motionId=Number(s.box_motion_id||0);if(lastBoxMotionId===null){lastBoxMotionId=motionId;displayedBoxRotation=Number(s.box_rotation||0);displayedBoxRotationY=Number(s.box_rotation_y||0);drawBox(displayedBoxRotation,displayedBoxRotationY,null);}else if(motionId!==lastBoxMotionId){lastBoxMotionId=motionId;animateBoxMotion(s.box_motion||[]);}document.getElementById('badge').textContent=s.running?'Test çalışıyor':(s.error?'Hata':'Hazır');document.getElementById('badge').className='badge'+(s.running?' on':'');document.getElementById('start').disabled=s.running;document.getElementById('stop').disabled=!s.running;document.getElementById('pn').disabled=s.running;document.getElementById('sn').disabled=s.running;let d=s.device||{};document.getElementById('deviceInfo').innerHTML=`<div class="device-item"><label>Etiket PN (pn_input)</label><strong>${esc(s.pn||'—')}</strong></div><div class="device-item"><label>Cihaz PN (pn_dvc)</label><strong>${esc(d.pn_dvc||'—')}</strong>${matchTag(d.pn_match)}</div><div class="device-item"><label>Etiket SN (sn_input)</label><strong>${esc(s.sn||'—')}</strong></div><div class="device-item"><label>Cihaz SN (sn_dvc)</label><strong>${esc(d.sn_dvc||'—')}</strong>${matchTag(d.sn_match)}</div><div class="device-item"><label>Bağlantı durumu</label><strong>${d.connection===true?'<span class="tag pass">Bağlandı</span>':d.connection===false?'<span class="tag fail">Bağlanamadı</span>':'<span class="tag">Bekleniyor</span>'}</strong></div><div class="device-item"><label>Kullanılan COM portları</label><strong>Standard: ${esc(d.standard_com||'—')}</strong><small>Enhanced: ${esc(d.enhanced_com||'—')}</small></div>`;document.getElementById('informationList').innerHTML=(s.information||[]).map(m=>'<li>'+esc(m)+'</li>').join('');document.getElementById('tests').innerHTML=Object.keys(labels).map(n=>{let t=s.tests[n],res=t.result===true?'<span class="result pass">Geçti</span>':t.result===false?'<span class="result fail">Kaldı</span>':'<span class="result">—</span>';return `<div class="test"><span class="num">${n}</span><span class="name">${labels[n]}</span><span class="status">${esc(t.status)}</span>${res}</div>`}).join('');let box=document.getElementById('logs');box.innerHTML=s.logs.length?s.logs.map(x=>`<div class="entry"><span class="time">${esc(x.time)}</span><span>${esc(x.text)}</span></div>`).join(''):'<span class="empty">Test başladığında Python çıktısı burada görünür.</span>';box.scrollTop=box.scrollHeight}
async function poll(){try{let r=await fetch('/api/status');render(await r.json())}catch(e){}setTimeout(poll,900)}
async function startRun(){boxAnimationId++;drawBox(0,0,null);lastBoxMotionId=0;displayedBoxRotation=0;displayedBoxRotationY=0;let pn=document.getElementById('pn').value.trim(),sn=document.getElementById('sn').value.trim();if(!pn||!sn){alert('Lütfen etiket PN ve SN değerlerini girin.');return}let r=await fetch('/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({pn,sn})});let d=await r.json();if(!r.ok)alert(d.error||'Başlatılamadı')}
async function stopRun(){if(!confirm('Test işlemini durdurmak istiyor musunuz?'))return;await fetch('/api/stop',{method:'POST'})}
drawBox(0,0,null);poll();</script></body></html>'''

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass
    def send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(status); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        if urlparse(self.path).path == "/api/status":
            with lock: data = json.loads(json.dumps(state))
            return self.send_json(data)
        if urlparse(self.path).path in ("/", "/index.html"):
            body = PAGE.encode("utf-8"); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(body))); self.send_header("Cache-Control", "no-store"); self.end_headers(); return self.wfile.write(body)
        self.send_error(404)
    def do_POST(self):
        global process, state
        route = urlparse(self.path).path
        if route == "/api/start":
            try: payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", "0"))))
            except Exception: return self.send_json({"error":"Geçersiz istek."}, 400)
            pn, sn = str(payload.get("pn", "")).strip(), str(payload.get("sn", "")).strip()
            if not pn or not sn: return self.send_json({"error":"PN ve SN girilmelidir."}, 400)
            with lock:
                if state["running"]: return self.send_json({"error":"Bir test zaten çalışıyor."}, 409)
                state = {"running": True, "pn": pn, "sn": sn, "device": {"pn_dvc": "Okunuyor…", "sn_dvc": "Okunuyor…", "pn_match": None, "sn_match": None, "connection": None, "standard_com": "Aranıyor…", "enhanced_com": "—"}, "information": [], "tests": {n: {"status":"Bekliyor", "result":None} for n,_ in TESTS}, "logs": [], "error":None, "started_at":time.time(), "box_rotation":0, "box_rotation_y":0, "box_motion_id":0, "box_motion":[]}
            env = os.environ.copy(); env["M2GR_LABEL_PN"] = pn; env["M2GR_LABEL_SN"] = sn; env["PYTHONUNBUFFERED"] = "1"
            try:
                process = subprocess.Popen([sys.executable, str(ROOT / "M2GR_main.py")], cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", bufsize=1, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                threading.Thread(target=monitor, args=(process,), daemon=True).start()
            except Exception as exc:
                with lock: state["running"] = False; state["error"] = str(exc)
                return self.send_json({"error":str(exc)}, 500)
            return self.send_json({"ok":True})
        if route == "/api/stop":
            with lock: proc = process
            if proc and proc.poll() is None:
                proc.terminate()
                add_log("Durdurma isteği gönderildi.")
            return self.send_json({"ok":True})
        self.send_error(404)

if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"M2GR GUI running at http://127.0.0.1:{PORT}", flush=True)
    server.serve_forever()



















