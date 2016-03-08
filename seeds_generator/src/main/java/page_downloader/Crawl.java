import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.transport.InetSocketTransportAddress;
import org.elasticsearch.client.Client;
import java.util.ArrayList;

public class Crawl {

    private ArrayList<String> urls = null;
    private String es_index = "memex";
    private String es_doc_type = "page";
    private String es_host = "localhost";
    private Client client = null;
    private int poolSize = 100;
    private ExecutorService crawlForwardService = Executors.newFixedThreadPool(poolSize);
    private ExecutorService crawlBackwardService = Executors.newFixedThreadPool(poolSize);
    private Download download = null;
    
    public Crawl(String es_index, String es_doc_type, String es_host){
	if(es_host.isEmpty())
	    es_host = "localhost";
	else {
	    String[] parts = es_host.split(":");
	    if (parts.length == 2)
		es_host = parts[0];
	    else if(parts.length == 3)
		es_host = parts[1];
	    
	    es_host = es_host.replaceAll("/","");
	}

	this.es_host = es_host;

	this.client = new TransportClient().addTransportAddress(new InetSocketTransportAddress(es_host, 9300));
	
	if(!es_index.isEmpty())
	    this.es_index = es_index;
	if(!es_doc_type.isEmpty())
	    this.es_doc_type = es_doc_type;
	
	this.download = new Download("Crawl: " + this.es_index, this.es_index, this.es_doc_type, this.es_host);
    }

    public void addForwardCrawlTask(ArrayList<String> urls){
	crawlForwardService.execute(new CrawlerInterface(urls, null, "forward", "", this.es_index, this.es_doc_type, this.client, this.download));
    }

    public void addBackwardCrawlTask(ArrayList<String> urls, String top){
	crawlBackwardService.execute(new CrawlerInterface(urls, null, "backward", top, this.es_index, this.es_doc_type, this.client, this.download));
    }

    public void shutdown(){
	try {
	    crawlForwardService.shutdown();
	    crawlBackwardService.shutdown();
	    crawlForwardService.awaitTermination(60 , TimeUnit.SECONDS);
	    crawlBackwardService.awaitTermination(60 , TimeUnit.SECONDS);
	    System.out.println("SHUTDOWN");
	    this.client.close();
	} catch (InterruptedException e) {
	    e.printStackTrace();
	}
    }

    
}
