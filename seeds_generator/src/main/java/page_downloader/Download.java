import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.util.concurrent.TimeUnit;


public class Download {

    private String inputFile = "";
    private String query = "";
    public Download(String filename, String query){
	this.inputFile = filename;
	this.query = query;
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
		    downloaderService.execute(new Download_URL(url.trim(), this.query));
		} 
		fr.close(); 
		downloaderService.shutdown();
		try {
		    //downloaderService.awaitTermination(Long.MAX_VALUE, TimeUnit.NANOSECONDS);
		    downloaderService.awaitTermination(60 , TimeUnit.SECONDS);
		    Download_URL.close();
		} catch (InterruptedException e) {
		    e.printStackTrace();
		}
	    } catch (IOException e) {
		e.printStackTrace();
	    } 
	}

    }
    
    public static void main(String[] args){
	Download d = new Download(args[0], args[1]);
	d.start();
	System.out.println("Download Finished");
	System.exit(0);
    }
}
