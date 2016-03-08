import java.util.regex.Pattern;
import java.util.regex.Matcher;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Map;
import java.net.URL;
import java.net.HttpURLConnection;
import java.io.InputStreamReader;
import java.io.BufferedReader;
import java.io.StringReader;
import org.apache.commons.codec.binary.Base64;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;
import org.xml.sax.InputSource;
import org.w3c.dom.*;

import org.elasticsearch.common.xcontent.XContentFactory;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.client.Client;
import org.elasticsearch.action.search.SearchResponse;
import org.elasticsearch.search.SearchHit; 
import org.elasticsearch.action.search.SearchType;
import org.elasticsearch.index.query.QueryBuilders;

public class CrawlerInterface implements Runnable{
    private static final Pattern linkPattern = Pattern.compile("\\s*(?i)href\\s*=\\s*(\"([^\"]*\")|'[^']*'|([^'\">\\s]+))",  Pattern.CASE_INSENSITIVE|Pattern.DOTALL);
    private static final String accountKey = "jgRfXs073p8B87c/TJamrnIDjbeyYtH5gAe7+TYvsIw";
    ArrayList<String> urls = null;
    ArrayList<String> html = null;
    String es_index = "memex";
    String es_doc_type = "page";
    String es_host = "localhost";
    Client client = null;
    String crawlType = "";
    String top = "10";
    Download download = null;
    
    public CrawlerInterface(ArrayList<String> urls, ArrayList<String> html, String crawl_type, String top, String es_index, String es_doc_type, String es_host, Client client){
	this.urls = urls;
	this.html = html;
	if(!es_index.isEmpty())
	    this.es_index = es_index;
	if(!es_doc_type.isEmpty())
	    this.es_doc_type = es_doc_type;
	this.es_host = es_host;
	this.client = client;
	this.crawlType = crawl_type;
	this.top = top;
	this.download = new Download("Crawl: " + this.es_index, this.es_index, this.es_doc_type, this.es_host);
    }

    public ArrayList<String> crawl_backward(ArrayList<String> urls, String count){
        /*Using backlink search to find more similar webpages
        *Args:
        *- urls: a list of relevant urls
        *Returns:
        *- res: a list of backlinks
        */   
        HashSet<String> links = new HashSet<String>();
        byte[] accountKeyBytes = Base64.encodeBase64((accountKey + ":" + accountKey).getBytes());
        String accountKeyEnc = new String(accountKeyBytes);
        String top = count;
        for (String url: urls){
            try{
                String query = "inbody:" + url;
                URL urlObj = new URL("https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Web?Query=%27" + query + "%27&$top="+ top);
                HttpURLConnection conn = (HttpURLConnection)urlObj.openConnection();
                conn.setRequestMethod("GET");
                conn.setRequestProperty("Authorization", "Basic " + accountKeyEnc);

                BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
                String output = "";
                String line;
                while ((line = br.readLine()) != null) {
                    output = output + line;
                }

                conn.disconnect();

                DocumentBuilderFactory docBuilderFactory = DocumentBuilderFactory.newInstance();
                DocumentBuilder docBuilder = docBuilderFactory.newDocumentBuilder(); 
                InputSource is = new InputSource(new StringReader(output));
                Document doc = docBuilder.parse(is);
                NodeList nls = doc.getElementsByTagName("d:Url");
                
                for(int i=0; i<nls.getLength(); i++){
                    Element e = (Element)nls.item(i);
                    NodeList nl = e.getChildNodes();
                    String u = nl.item(0).getNodeValue();
                    links.add(u);
                }
            }
            catch(Exception e){
                e.printStackTrace();
            }
        }
        
        ArrayList<String> res = new ArrayList<String>(links);

	System.out.println();
	System.out.println("Backlinks");
	System.out.println(res);
	System.out.println();

	for(String url: res){
	    if(urls.indexOf(url) == -1){
		System.out.println("Crawling forward " + url);
		System.out.println();
		String html = this.getContent(url);
		this.crawl_forward(url, html);
	    }
	}
        return res;
    }

    public ArrayList<String> crawl_forward(String url, String html){
        /*Extract and standarlize outlinks from the html
        *Args:
        *- url: 
        *- html: html content to be extracted
        *Returns:
        *- res: a list of urls extracted from html content
        */
        HashSet<String> links = new HashSet<String>();
        try{
            Matcher pageMatcher = linkPattern.matcher(html);
            String domain = "http://" + (new URL(url)).getHost();
            while(pageMatcher.find()){
                String link = pageMatcher.group(2);
                if (link != null){
                    //Validate and standarlize url
                    link = link.replaceAll("\"", "");
                    if (link.indexOf(".css") != -1)
                        continue;
                    if (link.startsWith("/"))
                        link = domain + link;
                    if (!link.startsWith("http://"))
                        continue;
                    links.add(link);
                }
            }
        } catch(Exception e) {
            e.printStackTrace();
        }
	
        ArrayList<String> res = new ArrayList<String>(links);
	for(String f_url: res){
	    this.download.addTask(f_url);
	}

        return res;
    }

    public void test_backlink(String seed, String top){
        ArrayList<String> urls = new ArrayList<String>();
        urls.add(seed);
        ArrayList<String> res = crawl_backward(urls, top);
       
    }

    public String getContent(String seed){
        try{
            URL url = new URL(seed);
            HttpURLConnection conn = (HttpURLConnection)url.openConnection();
            conn.setRequestMethod("GET");
            
            BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
            String output = "";
            String line;
            while ((line = br.readLine()) != null) {
                output = output + line;
            }
            conn.disconnect();

	    return output;

        } catch (Exception e){
            e.printStackTrace();
        }

	return "";
    }

    public void run() {
	if(this.crawlType.equals("backward")){
	    this.crawl_backward(this.urls, this.top);
	}
	else if(this.crawlType.equals("forward")){
	    for(int i=0; i < this.urls.size();++i){
		SearchResponse response = null;
		try{
		    response = client.prepareSearch(this.es_index)
			.setTypes(this.es_doc_type)
			.setSearchType(SearchType.DFS_QUERY_THEN_FETCH)
			.setFetchSource(new String[]{"html"}, null)
			.setQuery(QueryBuilders.termQuery("url", this.urls.get(i)))                 // Query
			.setFrom(0).setExplain(true)
			.execute()
			.actionGet();
		} catch (Throwable e) {
		    System.out.println(e);
		}

		if(response == null)
		    return;
		
		String html = "";
		for (SearchHit hit : response.getHits()) {
		    Map map = hit.getSource();
		    html = (String)map.get("html");
		}
		this.crawl_forward(this.urls.get(i), html);
	    }
	}
	this.download.shutdown();
    }
    
}
