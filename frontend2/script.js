// Slideshow
function startSlides(){
  const slides = document.querySelectorAll('.slide');
  let idx = 0;
  if(!slides || slides.length===0) return;
  setInterval(()=>{
    slides.forEach(s=>s.classList.remove('active'));
    slides[idx].classList.add('active');
    idx = (idx+1)%slides.length;
  },3000);
}
document.addEventListener('DOMContentLoaded', ()=>{
  startSlides();

  // Toggle login/register
  window.showRegister = ()=>{
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
    document.getElementById('panelTitle').innerText = 'Register';
  };
  window.showLogin = ()=>{
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('panelTitle').innerText = 'Login';
  };

  // Demo storage for users and donors
  const defaultUsers = [
    {name:'Ali Khan',cnic:'35201-1234567-8',blood:'A+',password:'admin',history:'Jan 2025',city:'Lahore'},
    {name:'Sara Ahmed',cnic:'35201-9876543-2',blood:'O-',password:'pass',history:'Feb 2025',city:'Karachi'}
  ];
  if(!localStorage.getItem('users')) localStorage.setItem('users', JSON.stringify(defaultUsers));

  // Register handler
  const reg = document.getElementById('registerForm');
  reg && reg.addEventListener('submit', function(e){
    e.preventDefault();
    const form = new FormData(reg);
    const user = Object.fromEntries(form.entries());
    const users = JSON.parse(localStorage.getItem('users')||'[]');
    users.push(user);
    localStorage.setItem('users', JSON.stringify(users));
    alert('Account created (demo). You can now login.');
    showLogin();
  });

  // Login handler (simple demo using CNIC or username)
  const login = document.getElementById('loginForm');
  login && login.addEventListener('submit', function(e){
    e.preventDefault();
    const form = new FormData(login);
    const username = form.get('username') || '';
    const password = form.get('password') || '';
    const users = JSON.parse(localStorage.getItem('users')||'[]');
    const found = users.find(u=> (u.cnic===username || u.name===username || u.username===username) && u.password===password );
    if(found){ window.location.href = 'dashboard.html'; }
    else alert('Invalid credentials (demo). Use sample accounts or register.');
  });

  // Check record by CNIC
  const checkForm = document.getElementById('checkForm');
  checkForm && checkForm.addEventListener('submit', function(e){
    e.preventDefault();
    const cnic = document.getElementById('checkCnic').value.trim();
    const users = JSON.parse(localStorage.getItem('users')||'[]');
    const u = users.find(x=> x.cnic===cnic );
    const out = document.getElementById('recordResult');
    if(u){
      out.innerHTML = `<div class="record"><strong>${u.name}</strong><p>CNIC: ${u.cnic}</p><p>Blood Group: ${u.blood}</p><p>Recent Donation: ${u.history}</p></div>`;
    } else {
      out.innerHTML = '<p class="muted">No record found for that CNIC.</p>';
    }
  });

  // Donor records page load
  if(document.getElementById('donorTable')){
    const users = JSON.parse(localStorage.getItem('users')||'[]');
    const tbody = document.querySelector('#donorTable tbody');
    users.forEach(u=>{
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${u.name||''}</td><td>${u.cnic||''}</td><td>${u.blood||''}</td><td>${u.city||''}</td><td>${u.history||''}</td>`;
      tbody.appendChild(tr);
    });
    // Add donor form
    const addForm = document.getElementById('addDonorForm');
    addForm && addForm.addEventListener('submit', function(e){
      e.preventDefault();
      const form = new FormData(addForm);
      const d = Object.fromEntries(form.entries());
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${d.name}</td><td>${d.cnic}</td><td>${d.bloodGroup}</td><td>${d.city}</td><td>${d.last}</td>`;
      tbody.appendChild(tr);
      const users = JSON.parse(localStorage.getItem('users')||'[]');
      users.push({name:d.name,cnic:d.cnic,blood:d.bloodGroup,city:d.city,history:d.last});
      localStorage.setItem('users', JSON.stringify(users));
      addForm.reset();
    });
  }

  // Patient request form (demo)
  const pform = document.getElementById('patientForm');
  pform && pform.addEventListener('submit', function(e){
    e.preventDefault();
    alert('Request submitted (demo).');
    pform.reset();
  });

  // Export CSV
  const exportBtn = document.getElementById('exportCsv');
  exportBtn && exportBtn.addEventListener('click', function(){
    const table = document.getElementById('stockTable');
    if(!table) return;
    const rows = Array.from(table.querySelectorAll('tr'));
    const csv = rows.map(r=> Array.from(r.querySelectorAll('th,td')).map(c=>`"${c.innerText.replace(/"/g,'""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], {type:'text/csv'});
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'blood_stock.csv'; document.body.appendChild(a); a.click(); a.remove();
  });

  // Emergency search
  const emergencyForm = document.getElementById('emergencyForm');
  emergencyForm && emergencyForm.addEventListener('submit', function(e){
    e.preventDefault();
    const form = new FormData(emergencyForm);
    const blood = form.get('bloodGroup');
    const city = form.get('city');
    // Dummy filter from users list
    const users = JSON.parse(localStorage.getItem('users')||'[]');
    const matches = users.filter(u=> u.blood===blood && (!city || (u.city && u.city.toLowerCase().includes(city.toLowerCase()))));
    const out = document.getElementById('donorResults');
    if(matches.length===0) out.innerHTML = '<p class="muted">No donors found (demo).</p>';
    else out.innerHTML = '<ul>' + matches.map(m=>`<li>${m.name} — ${m.city || 'City'} — ${m.blood}</li>`).join('') + '</ul>';
  });

  // Chatbot form
  const chatForm = document.getElementById('chatForm');
  chatForm && chatForm.addEventListener('submit', function(e){
    e.preventDefault();
    const q = document.getElementById('chatInput').value || '';
    const win = document.getElementById('chatWindow');
    let ans = 'Sorry, try: "Check A+ availability" or "Register as donor".';
    if(q.toLowerCase().includes('a+')) ans = 'A+ availability: City Hospital — 12 units (demo).';
    if(q.toLowerCase().includes('register')) ans = 'To register: use the Register form on the main page.';
    win.innerHTML += `<p><b>You:</b> ${q}</p><p><b>Bot:</b> ${ans}</p>`;
    document.getElementById('chatInput').value = '';
  });

});
