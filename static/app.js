document.addEventListener('DOMContentLoaded', ()=>{
  const q = document.getElementById('query');
  const btn = document.getElementById('btn');
  const result = document.getElementById('result');
  const title = document.getElementById('title');
  const openLink = document.getElementById('openLink');
  const downloadLink = document.getElementById('downloadLink');
  const pdfFrame = document.getElementById('pdfFrame');
  const msg = document.getElementById('message');

  function showMessage(text){msg.textContent = text}

  async function doSearch(){
    const query = q.value.trim();
    if(!query){ showMessage('Please enter a query.'); return }
    showMessage('Searching...');
    try{
      const res = await fetch('/api/search', {
        method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({query})
      });
      const data = await res.json();
      if(!res.ok){ showMessage(data.error || 'Search failed'); return }
      title.textContent = data.name;
      openLink.href = data.url;
      pdfFrame.src = data.url;
      downloadLink.href = data.download_url || data.url;
      result.classList.remove('hidden');
      showMessage('');
    }catch(e){ showMessage('Network error') }
  }

  btn.addEventListener('click', doSearch);
  q.addEventListener('keydown', (e)=>{ if(e.key === 'Enter') doSearch() });
});
