import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.util.concurrent.TimeUnit;
import org.elasticsearch.client.transport.TransportClient;
import org.elasticsearch.common.transport.InetSocketTransportAddress;
import org.elasticsearch.client.Client;

public class Download {

    private String inputFile = "";
    private String query = "";
    private String es_index = "memex";
    private String es_doc_type = "page";
    private Client client = null;

    public Download(String filename, String query, String es_index, String es_doc_type, String es_host){
	this.inputFile = filename;
	this.query = query;
	if(es_host.isEmpty())
	    es_host = "localhost";
	this.client = new TransportClient().addTransportAddress(new InetSocketTransportAddress(es_host, 9300));

	if(!es_index.isEmpty())
	    this.es_index = es_index;
	if(!es_doc_type.isEmpty())
	    this.es_doc_type = es_doc_type;
    }

    public void start(){
	
	int poolSize = Runtime.getRuntime().availableProcessors();
	poolSize = 101;
	ExecutorService downloaderService = Executors.newFixedThreadPool(poolSize-1);
	
	if(!inputFile.equals("")){
	    try {
		FileReader fr = new FileReader(this.inputFile); 
		BufferedReader br = new BufferedReader(fr); 
		String url; 
		while((url = br.readLine()) != null) { 
		    downloaderService.execute(new Download_URL(url.trim(), this.query, this.es_index, this.es_doc_type, this.client));
		} 
		fr.close(); 
		downloaderService.shutdown();
		try {
		    //downloaderService.awaitTermination(Long.MAX_VALUE, TimeUnit.NANOSECONDS);
		    downloaderService.awaitTermination(60 , TimeUnit.SECONDS);
		    this.client.close();
		} catch (InterruptedException e) {
		    e.printStackTrace();
		}
	    } catch (IOException e) {
		e.printStackTrace();
	    } 
	}

    }
    
    public static void main(String[] args){
	Download d = new Download(args[0], args[1], args[2], args[3], args[4]);
	d.start();
	System.out.println("Download Finished");
	System.exit(0);
    }
}
