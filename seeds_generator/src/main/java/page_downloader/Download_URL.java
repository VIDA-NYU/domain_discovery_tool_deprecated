import java.io.IOException;

import org.apache.http.HttpEntity;
import org.apache.http.HttpResponse;
import org.apache.http.Header;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpUriRequest;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.util.EntityUtils;

import org.apache.commons.codec.binary.Base64;

import org.elasticsearch.common.xcontent.XContentFactory;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.transport.InetSocketTransportAddress;
import org.elasticsearch.client.Client;


import org.elasticsearch.action.index.IndexResponse;

public class Download_URL implements Runnable {
    String url = "";

    public Download_URL(String url){
	this.url = url;
    }

    public void run() {
	//Do not process pdf files
	if(this.url.contains(".pdf"))
	    return;

	CloseableHttpClient httpclient = HttpClients.createDefault();
	// Perform a GET request
	HttpUriRequest request = new HttpGet(url);
	
	System.out.println("Executing request " + request.getURI());
	
	String elasticServer = "localhost";
	if(System.getenv("ELASTICSEARCH_SERVER") != null)
	    elasticServer = System.getenv("ELASTICSEARCH_SERVER");
	
	Client client = new TransportClient()
	    .addTransportAddress(new InetSocketTransportAddress(elasticServer, 9300));
	
	HttpResponse response = null;
	try{
	    response = httpclient.execute(request);
	    int status = response.getStatusLine().getStatusCode();
	    if (status >= 200 && status < 300) {
		HttpEntity entity = response.getEntity();
		if(entity != null){
		    String responseBody = EntityUtils.toString(entity);
		    String content_type = response.getFirstHeader("Content-Type").getValue();
		    Integer content_length = (response.getFirstHeader("Content-Length") != null) ? Integer.valueOf(response.getFirstHeader("Content-Length").getValue()) : responseBody.length();
		    String date = response.getFirstHeader("Date").getValue();
		    String content_text = "";
		    if(!content_type.contains("pdf")){
			Extract extract = new Extract();
			content_text = extract.process(responseBody);
		    }

	
		    IndexResponse indexresponse = client.prepareIndex("memex", "page")
			.setSource(XContentFactory.jsonBuilder()
				   .startObject()
				   .field("url", request.getURI())
				   .field("html", Base64.encodeBase64(responseBody.getBytes()))
				   .field("text", content_text)
				   .field("length", content_length)
				   .endObject()
				   )
			.execute()
			.actionGet();

		}
	    } else {
		throw new ClientProtocolException("Unexpected response status: " + status);
	    }

	} catch (ClientProtocolException e1) {
	    // TODO Auto-generated catch block
	    e1.printStackTrace();
	} catch (IOException e1) {
	    // TODO Auto-generated catch block
	    e1.printStackTrace();
	} finally {
	    try{
		httpclient.close();
		client.close();
	    } catch (IOException e){
		e.printStackTrace();
	    }
        }
    }
}
