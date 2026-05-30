const {chromium} = require('playwright');
(async () => {
  const b = await chromium.launch({headless:true});
  const p = await b.newPage();
  await p.goto('http://192.168.9.1/login.htm', {waitUntil:'networkidle', timeout:20000});
  await p.waitForTimeout(500);
  const loginResp = await p.evaluate(async () => {
    const r = await fetch('/', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({method:'do',login:{username:'admin',password:'0rZglJbA9TefbwK'}})});
    return r.json();
  });
  const stok = loginResp.stok;
  console.log('stok:', stok);
  const names = ['wan2_phy','wan2_conf','wan_info_2','ppp_status_wan2','wan2_ipaddr','wan2_info_all','dual_wan','wan2_dns','wan_port_info','wan_status','wan2_pppoe'];
  for(const n of names) {
    const r = await p.evaluate(async ({s,name}) => {
      const resp = await fetch('/stok='+s+'/ds', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({method:'get',network:{name:name}})});
      return resp.json();
    }, {s:stok,name:n});
    console.log(n+':', JSON.stringify(r).substring(0,200));
  }
  await b.close();
})().catch(e => console.error(e));
