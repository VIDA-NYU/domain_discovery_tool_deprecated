import java.io.*;
import de.l3s.boilerpipe.extractors.ArticleExtractor;
import java.net.URL;
import java.util.*;
import java.util.HashMap;
import java.lang.String;
import java.net.URLDecoder;
import java.io.PrintWriter;

public class Extract {
    public  void  process(String content)
    {
	try{
	    if(!content.contains("@empty@")){
		content = ArticleExtractor.INSTANCE.getText(content);
	    }
	    content = content.trim().replaceAll(" +", " ");
	    content = content.replaceAll("[\n\"\t]", " ");
	    content = content.replaceAll(",","");
	    content = content.toLowerCase();
	    System.out.println(content);
	}
	catch(Exception e){
	    System.out.println("process Exception" + e.getMessage());
	}
     
    }

    public static void main(String[] args) {
	Extract e = new Extract();

	try{
	    BufferedReader br = 
		new BufferedReader(new InputStreamReader(System.in));
	    
	    String html = "";
	    String input;

	    while((input=br.readLine())!=null){
		html += input;
	    }

	    e.process(html);
	    
	}catch(IOException io){
	    io.printStackTrace();
	}
    }
}
