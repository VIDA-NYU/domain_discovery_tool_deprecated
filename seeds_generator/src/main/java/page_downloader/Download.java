import java.util.concurrent.Executors;
import java.util.concurrent.ExecutorService;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;


public class Download {

    private String inputFile = "";
    public Download(String filename){
	this.inputFile = filename;
    }

    public void start(){
	
	int poolSize = Runtime.getRuntime().availableProcessors();
	ExecutorService downloaderService = Executors.newFixedThreadPool(poolSize-1);
	
	
	if(!inputFile.equals("")){
	    try {
	
		FileReader fr = new FileReader(this.inputFile); 
		BufferedReader br = new BufferedReader(fr); 
		String url; 
		while((url = br.readLine()) != null) { 
		    downloaderService.execute(new Download_URL(url.trim()));
		} 
		fr.close(); 
		downloaderService.shutdown();
	    } catch (IOException e) {
		e.printStackTrace();
	    } 
	}

    }
    
    public static void main(String[] args){
	Download d = new Download(args[0]);
	d.start();
    }
}
