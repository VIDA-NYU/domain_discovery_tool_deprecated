import java.util.concurrent.Executors;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.ExecutorService;

public class Download {

    private String inputFile = "";
    public void Download(String filename){
	this.inputFile = filename;
    }
    
    public void start(){
	if(!"".equals(inputFile)){
	    
	    try {
		FileReader fr = new FileReader(this.inputFile); 
		BufferedReader br = new BufferedReader(fr); 
		String url; 
		while((url = br.readLine()) != null) { 
		    System.out.println(s); 
		} 
		fr.close(); 

	    } catch (IOException e) {
		e.printStackTrace();
	    }
	}
    }
}
