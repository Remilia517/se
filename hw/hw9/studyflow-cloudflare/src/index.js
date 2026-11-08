const HTML = String.raw`<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>StudyFlow 2.0｜學生任務管理系統</title>
<style>
:root{font-family:Arial,"Noto Sans TC",sans-serif;color:#1f2937;background:#f4f6fb}
*{box-sizing:border-box}
body{margin:0}
button,input,select,textarea{font:inherit}
header{background:#243b6b;color:white;padding:26px max(22px,calc((100% - 1120px)/2))}
header h1{margin:0 0 6px;font-size:28px}
header p{margin:0;color:#dbeafe}
main{max-width:1120px;margin:26px auto;padding:0 18px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px}
.stat,.panel{background:white;border:1px solid #e5e9f2;border-radius:14px;padding:18px;box-shadow:0 3px 12px #1e293b08}
.stat span{color:#64748b;font-size:13px}
.stat strong{display:block;font-size:28px;margin-top:7px;color:#243b6b}
.layout{display:grid;grid-template-columns:minmax(280px,.85fr) minmax(0,1.6fr);gap:18px}
h2{font-size:18px;margin:0 0 15px}
.field{margin-bottom:12px}
.field label{display:block;font-size:13px;color:#475569;margin-bottom:5px}
input,select,textarea{width:100%;padding:10px 11px;border:1px solid #d8deea;border-radius:8px;background:white}
textarea{resize:vertical;min-height:76px}
.btn{border:0;border-radius:8px;padding:10px 14px;background:#3159a5;color:white;cursor:pointer}
.btn:hover{filter:brightness(.94)}
.btn.secondary{background:#e8edf7;color:#243b6b}
.btn.danger{background:#b93838}
.actions{display:flex;gap:8px;flex-wrap:wrap}
.filters{display:grid;grid-template-columns:1.5fr 1fr 1fr;gap:8px;margin-bottom:14px}
.task{border:1px solid #e5e9f2;border-radius:10px;padding:13px;margin-bottom:10px}
.taskhead{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
.task h3{font-size:15px;margin:0 0 5px}
.meta{font-size:12px;color:#64748b;line-height:1.7}
.desc{font-size:13px;color:#475569;margin:8px 0;white-space:pre-wrap}
.pill{font-size:11px;border-radius:20px;padding:4px 8px;background:#eef2ff;color:#344b86;white-space:nowrap}
.pill.done{background:#dcfce7;color:#166534}
.pill.high{background:#fee2e2;color:#991b1b}
.empty{text-align:center;padding:35px 10px;color:#94a3b8}
.calendar{display:grid;grid-template-columns:repeat(7,1fr);gap:5px;margin-top:12px}
.day{min-height:65px;background:#f8fafc;border:1px solid #e5e9f2;border-radius:7px;padding:5px;font-size:12px}
.day b{display:block;margin-bottom:4px}
.day small{display:block;color:#3159a5;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.notice{font-size:12px;color:#64748b;margin-top:12px}
.error{color:#b91c1c;font-size:13px;margin-top:8px}
@media(max-width:760px){
.stats{grid-template-columns:repeat(2,1fr)}
.layout{grid-template-columns:1fr}
.filters{grid-template-columns:1fr}
}
</style>
</head>
<body>
<header>
<h1>StudyFlow 2.0</h1>
<p>學生課程與任務管理系統｜Cloudflare Workers + D1</p>
</header>

<main>
<section class="stats">
<div class="stat"><span>全部任務</span><strong id="total">0</strong></div>
<div class="stat"><span>待處理</span><strong id="pending">0</strong></div>
<div class="stat"><span>進行中</span><strong id="progress">0</strong></div>
<div class="stat"><span>已完成</span><strong id="completed">0</strong></div>
</section>

<section class="layout">
<div class="panel">
<h2 id="formTitle">新增任務</h2>

<form id="taskForm">
<input type="hidden" id="taskId">

<div class="field">
<label for="title">任務名稱 *</label>
<input id="title" required maxlength="120" placeholder="例如：完成資料庫作業">
</div>

<div class="field">
<label for="course">課程名稱</label>
<input id="course" maxlength="80" placeholder="例如：人工智慧實務">
</div>

<div class="field">
<label for="description">任務說明</label>
<textarea id="description" placeholder="輸入任務內容或備註"></textarea>
</div>

<div class="field">
<label for="due_date">截止日期</label>
<input id="due_date" type="date">
</div>

<div class="field">
<label for="priority">優先程度</label>
<select id="priority">
<option value="低">低</option>
<option value="中" selected>中</option>
<option value="高">高</option>
</select>
</div>

<div class="field">
<label for="status">任務狀態</label>
<select id="status">
<option value="待處理">待處理</option>
<option value="進行中">進行中</option>
<option value="已完成">已完成</option>
</select>
</div>

<div class="actions">
<button class="btn" type="submit">儲存任務</button>
<button class="btn secondary" type="button" id="resetBtn">清除</button>
</div>
<div id="formError" class="error"></div>
</form>

<p class="notice">資料會儲存在 Cloudflare D1 資料庫。</p>
</div>

<div>
<section class="panel">
<h2>任務清單</h2>

<div class="filters">
<input id="search" placeholder="搜尋任務或課程…">
<select id="statusFilter">
<option value="">所有狀態</option>
<option>待處理</option>
<option>進行中</option>
<option>已完成</option>
</select>
<select id="priorityFilter">
<option value="">所有優先程度</option>
<option>高</option>
<option>中</option>
<option>低</option>
</select>
</div>

<div class="actions" style="margin-bottom:12px">
<button class="btn secondary" id="exportBtn" type="button">匯出 CSV</button>
<button class="btn secondary" id="reloadBtn" type="button">重新載入</button>
</div>

<div id="taskList"><div class="empty">載入中…</div></div>
<div id="listError" class="error"></div>
</section>

<section class="panel" style="margin-top:18px">
<h2>本月截止日曆</h2>
<div id="calendar" class="calendar"></div>
</section>
</div>
</section>
</main>

<script>
(function(){
  var tasks = [];
  var $ = function(id){ return document.getElementById(id); };

  function escapeHtml(value){
    return String(value == null ? '' : value).replace(/[&<>"']/g,function(ch){
      return {
        '&':'&amp;',
        '<':'&lt;',
        '>':'&gt;',
        '"':'&quot;',
        "'":'&#39;'
      }[ch];
    });
  }

  async function api(path, options){
    var response = await fetch(path, options || {});
    var data = await response.json().catch(function(){ return {}; });
    if(!response.ok){
      throw new Error(data.error || ('HTTP ' + response.status));
    }
    return data;
  }

  function resetForm(){
    $('taskForm').reset();
    $('taskId').value='';
    $('formTitle').textContent='新增任務';
    $('priority').value='中';
    $('status').value='待處理';
    $('formError').textContent='';
  }

  function updateStats(){
    $('total').textContent=tasks.length;
    $('pending').textContent=tasks.filter(function(t){
      return t.status==='待處理';
    }).length;
    $('progress').textContent=tasks.filter(function(t){
      return t.status==='進行中';
    }).length;
    $('completed').textContent=tasks.filter(function(t){
      return t.status==='已完成';
    }).length;
  }

  function renderTasks(){
    var q=$('search').value.trim().toLowerCase();
    var s=$('statusFilter').value;
    var p=$('priorityFilter').value;

    var filtered=tasks.filter(function(t){
      var hay=(t.title+' '+(t.course||'')+' '+(t.description||'')).toLowerCase();
      return (!q||hay.indexOf(q)>=0)&&
             (!s||t.status===s)&&
             (!p||t.priority===p);
    });

    if(!filtered.length){
      $('taskList').innerHTML='<div class="empty">目前沒有符合條件的任務</div>';
      return;
    }

    $('taskList').innerHTML=filtered.map(function(t){
      var statusClass=t.status==='已完成'?'done':'';
      var priorityClass=t.priority==='高'?'high':'';

      return '<article class="task">'+
        '<div class="taskhead">'+
          '<div>'+
            '<h3>'+escapeHtml(t.title)+'</h3>'+
            '<div class="meta">'+
              escapeHtml(t.course||'未分類課程')+
              '　｜　截止：'+escapeHtml(t.due_date||'未設定')+
            '</div>'+
          '</div>'+
          '<div>'+
            '<span class="pill '+statusClass+'">'+escapeHtml(t.status)+'</span> '+
            '<span class="pill '+priorityClass+'">'+escapeHtml(t.priority)+'優先</span>'+
          '</div>'+
        '</div>'+
        (t.description?
          '<div class="desc">'+escapeHtml(t.description)+'</div>':'')+
        '<div class="actions">'+
          '<button class="btn secondary" data-edit="'+t.id+'">編輯</button>'+
          '<button class="btn secondary" data-toggle="'+t.id+'">'+
            (t.status==='已完成'?'改為待處理':'標記完成')+
          '</button>'+
          '<button class="btn danger" data-delete="'+t.id+'">刪除</button>'+
        '</div>'+
      '</article>';
    }).join('');
  }

  function renderCalendar(){
    var now=new Date();
    var year=now.getFullYear();
    var month=now.getMonth();
    var first=new Date(year,month,1);
    var days=new Date(year,month+1,0).getDate();

    var labels=['日','一','二','三','四','五','六'];
    var html=labels.map(function(x){
      return '<div class="meta" style="text-align:center">'+x+'</div>';
    }).join('');

    for(var i=0;i<first.getDay();i++){
      html+='<div class="day"></div>';
    }

    for(var d=1;d<=days;d++){
      var date=year+'-'+String(month+1).padStart(2,'0')+'-'+
               String(d).padStart(2,'0');

      var matches=tasks.filter(function(t){
        return t.due_date===date;
      });

      html+='<div class="day"><b>'+d+'</b>'+
        matches.slice(0,3).map(function(t){
          return '<small title="'+escapeHtml(t.title)+'">'+
            escapeHtml(t.title)+'</small>';
        }).join('')+
        '</div>';
    }

    $('calendar').innerHTML=html;
  }

  async function loadTasks(){
    $('listError').textContent='';

    try{
      var data=await api('/api/tasks');
      tasks=data.tasks||[];
      updateStats();
      renderTasks();
      renderCalendar();
    }catch(err){
      $('listError').textContent='載入失敗：'+err.message;
      $('taskList').innerHTML=
        '<div class="empty">無法載入資料，請確認 D1 設定與資料表</div>';
    }
  }

  $('taskForm').addEventListener('submit',async function(e){
    e.preventDefault();
    $('formError').textContent='';

    var id=$('taskId').value;

    var payload={
      title:$('title').value.trim(),
      course:$('course').value.trim(),
      description:$('description').value.trim(),
      due_date:$('due_date').value,
      priority:$('priority').value,
      status:$('status').value
    };

    if(!payload.title){
      $('formError').textContent='請輸入任務名稱';
      return;
    }

    try{
      await api(id?('/api/tasks/'+id):'/api/tasks',{
        method:id?'PUT':'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(payload)
      });

      resetForm();
      await loadTasks();
    }catch(err){
      $('formError').textContent='儲存失敗：'+err.message;
    }
  });

  $('taskList').addEventListener('click',async function(e){
    var edit=e.target.getAttribute('data-edit');
    var toggle=e.target.getAttribute('data-toggle');
    var del=e.target.getAttribute('data-delete');

    if(edit){
      var t=tasks.find(function(x){
        return String(x.id)===edit;
      });

      if(!t)return;

      $('taskId').value=t.id;
      $('title').value=t.title;
      $('course').value=t.course||'';
      $('description').value=t.description||'';
      $('due_date').value=t.due_date||'';
      $('priority').value=t.priority||'中';
      $('status').value=t.status||'待處理';
      $('formTitle').textContent='編輯任務';

      window.scrollTo({top:0,behavior:'smooth'});
    }

    else if(toggle){
      var item=tasks.find(function(x){
        return String(x.id)===toggle;
      });

      if(!item)return;

      try{
        await api('/api/tasks/'+toggle,{
          method:'PATCH',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify({
            status:item.status==='已完成'?'待處理':'已完成'
          })
        });

        await loadTasks();
      }catch(err){
        $('listError').textContent='更新失敗：'+err.message;
      }
    }

    else if(del){
      if(!confirm('確定要刪除此任務嗎？'))return;

      try{
        await api('/api/tasks/'+del,{method:'DELETE'});
        await loadTasks();
      }catch(err){
        $('listError').textContent='刪除失敗：'+err.message;
      }
    }
  });

  $('resetBtn').addEventListener('click',resetForm);
  $('reloadBtn').addEventListener('click',loadTasks);

  $('exportBtn').addEventListener('click',function(){
    window.location.href='/api/export.csv';
  });

  ['search','statusFilter','priorityFilter'].forEach(function(id){
    $(id).addEventListener('input',renderTasks);
  });

  loadTasks();
})();
</script>
</body>
</html>`;

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status: status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "no-store"
    }
  });
}

function csvCell(value) {
  const text = String(value ?? "");
  return '"' + text.replace(/"/g, '""') + '"';
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // 健康檢查
    if (path === "/api/health" && request.method === "GET") {
      try {
        const result = await env.studyflow_db
          .prepare("SELECT COUNT(*) AS count FROM tasks")
          .first();

        return json({
          status: "ok",
          database: "connected",
          task_count: result?.count ?? 0
        });
      } catch (error) {
        return json({
          status: "error",
          database: "unavailable",
          error: error.message
        }, 500);
      }
    }

    // 查詢全部任務
    if (path === "/api/tasks" && request.method === "GET") {
      try {
        const result = await env.studyflow_db.prepare(
          `SELECT id, title, course, description, due_date,
                  priority, status, created_at, updated_at
           FROM tasks
           ORDER BY
             CASE WHEN due_date IS NULL OR due_date = '' THEN 1 ELSE 0 END,
             due_date ASC,
             id DESC`
        ).all();

        return json({ tasks: result.results || [] });
      } catch (error) {
        return json({ error: error.message }, 500);
      }
    }

    // 新增任務
    if (path === "/api/tasks" && request.method === "POST") {
      try {
        const body = await request.json();
        const title = String(body.title || "").trim();

        if (!title) {
          return json({ error: "任務名稱不可空白" }, 400);
        }

        const now = new Date().toISOString();

        const result = await env.studyflow_db.prepare(
          `INSERT INTO tasks
           (title, course, description, due_date, priority, status, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`
        ).bind(
          title,
          body.course || "",
          body.description || "",
          body.due_date || "",
          body.priority || "中",
          body.status || "待處理",
          now,
          now
        ).run();

        return json({
          success: true,
          id: result.meta?.last_row_id
        });
      } catch (error) {
        return json({ error: error.message }, 500);
      }
    }

    // 單筆任務：編輯、更新、刪除
    const taskMatch = path.match(/^\/api\/tasks\/(\d+)$/);

    if (taskMatch) {
      const id = Number(taskMatch[1]);

      // 完整編輯
      if (request.method === "PUT") {
        try {
          const body = await request.json();
          const title = String(body.title || "").trim();

          if (!title) {
            return json({ error: "任務名稱不可空白" }, 400);
          }

          await env.studyflow_db.prepare(
            `UPDATE tasks
             SET title = ?, course = ?, description = ?, due_date = ?,
                 priority = ?, status = ?, updated_at = ?
             WHERE id = ?`
          ).bind(
            title,
            body.course || "",
            body.description || "",
            body.due_date || "",
            body.priority || "中",
            body.status || "待處理",
            new Date().toISOString(),
            id
          ).run();

          return json({ success: true });
        } catch (error) {
          return json({ error: error.message }, 500);
        }
      }

      // 快速更新狀態
      if (request.method === "PATCH") {
        try {
          const body = await request.json();

          const allowed = ["status", "priority"];
          const key = allowed.find(function(item) {
            return Object.prototype.hasOwnProperty.call(body, item);
          });

          if (!key) {
            return json({ error: "沒有可更新的欄位" }, 400);
          }

          await env.studyflow_db.prepare(
            "UPDATE tasks SET " + key + " = ?, updated_at = ? WHERE id = ?"
          ).bind(
            body[key],
            new Date().toISOString(),
            id
          ).run();

          return json({ success: true });
        } catch (error) {
          return json({ error: error.message }, 500);
        }
      }

      // 刪除任務
      if (request.method === "DELETE") {
        try {
          await env.studyflow_db.prepare(
            "DELETE FROM tasks WHERE id = ?"
          ).bind(id).run();

          return json({ success: true });
        } catch (error) {
          return json({ error: error.message }, 500);
        }
      }
    }

    // 匯出 CSV
    if (path === "/api/export.csv" && request.method === "GET") {
      try {
        const result = await env.studyflow_db.prepare(
          `SELECT id, title, course, description, due_date,
                  priority, status, created_at
           FROM tasks ORDER BY id`
        ).all();

        const rows = [[
          "ID", "任務名稱", "課程", "說明",
          "截止日期", "優先程度", "狀態", "建立時間"
        ]];

        for (const task of (result.results || [])) {
          rows.push([
            task.id,
            task.title,
            task.course,
            task.description,
            task.due_date,
            task.priority,
            task.status,
            task.created_at
          ]);
        }

        const csv = "\uFEFF" +
          rows.map(function(row) {
            return row.map(csvCell).join(",");
          }).join("\r\n");

        return new Response(csv, {
          headers: {
            "Content-Type": "text/csv; charset=utf-8",
            "Content-Disposition":
              'attachment; filename="studyflow-tasks.csv"'
          }
        });
      } catch (error) {
        return json({ error: error.message }, 500);
      }
    }

    // 首頁：直接由 Worker 回傳 HTML
    if (path === "/" || path === "/index.html") {
      return new Response(HTML, {
        headers: {
          "Content-Type": "text/html; charset=utf-8",
          "Cache-Control": "no-store"
        }
      });
    }

    return new Response("Not Found", { status: 404 });
  }
};