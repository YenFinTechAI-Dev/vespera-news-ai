export function discoveryError(status:number,vi:boolean):string {
 const messages:Record<number,[string,string]>={
  403:['Yêu cầu tìm kiếm bị từ chối. Hãy tải lại trang.','Search request rejected. Please reload the page.'],
  429:['Tìm kiếm đang bận hoặc tạm giới hạn. Vui lòng thử lại sau một phút.','Search is busy or temporarily rate limited. Retry in one minute.'],
  502:['Nguồn tìm kiếm tạm không phản hồi. Vui lòng thử lại.','Search providers are temporarily unavailable. Please retry.'],
  503:['Chưa kết nối được máy chủ tìm kiếm. Vui lòng thử lại.','Cannot reach the search server. Please retry.'],
  504:['Máy chủ tìm kiếm phản hồi quá lâu. Vui lòng thử lại.','The search server timed out. Please retry.']
 };
 const message=messages[status]||['Không hoàn tất được tìm kiếm. Vui lòng thử lại.','Search could not complete. Please retry.'];
 return message[vi?0:1]+(status?` (${status})`:'');
}
function pause(ms:number,signal:AbortSignal){
 return new Promise<void>((resolve,reject)=>{
  const abort=()=>{clearTimeout(timer);reject(new DOMException('Aborted','AbortError'))};
  const timer=setTimeout(()=>{signal.removeEventListener('abort',abort);resolve()},ms);
  signal.addEventListener('abort',abort,{once:true});
  if(signal.aborted)abort();
 });
}
export async function discoverTopic(body:{query:string;language:string;mode:string},signal:AbortSignal){
 let status=0;
 for(let attempt=0;attempt<3;attempt++){
  signal.throwIfAborted();
  try{
   const response=await fetch('/api/news/discover',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal});
   status=response.status;
   if(response.ok){const data=await response.json();if(!Array.isArray(data.items))throw Error('Invalid search response');return data;}
   if(![429,502,503,504].includes(status))break;
  }catch(error){if(signal.aborted)throw error;status=0;}
  if(attempt<2)await pause(status===429?30000:3000*(attempt+1),signal);
 }
 throw Error(discoveryError(status,body.language==='vi'));
}
