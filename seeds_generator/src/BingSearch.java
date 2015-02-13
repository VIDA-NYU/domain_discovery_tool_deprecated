import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.InputStream;
import java.io.StringReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.util.Properties;
import java.util.ArrayList;
import org.apache.commons.codec.binary.Base64;
import org.xml.sax.InputSource;
import org.w3c.dom.*;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.DocumentBuilder;

public class BingSearch {
    
  private String accountKey;
  private Properties prop; 

  public BingSearch(){
    try{
        prop = new Properties();
        prop.load(getClass().getClassLoader().getResourceAsStream("conf/config.properties"));
        //accountKey = "jgRfXs073p8B87c/TJamrnIDjbeyYtH5gAe7+TYvsIw";
        accountKey = prop.getProperty("ACCOUNTKEY");
    }   
    catch(Exception e){
        prop = null;
    }
  } 

  public ArrayList<String> read_queries(String queryfile){
    ArrayList<String> queries = new ArrayList<String>();
    try{
      File file = new File(queryfile);
      FileReader fileReader = new FileReader(file);
      BufferedReader bufferedReader = new BufferedReader(fileReader);
      String line;
      while ((line = bufferedReader.readLine()) != null) {
        queries.add(line);
      }
      fileReader.close();
    }
    catch(Exception e){
        e.printStackTrace();
    }
    return queries;
  }

  public ArrayList<String> search(String query, String top){
    System.out.println("Query: " + query);
    if (this.prop == null){
        System.out.println("Error: config file is not loaded yet");
        return null;
    }
    ArrayList<String> results = new ArrayList<String>();
    query = query.replaceAll(" ", "%20");
    //String accountKey="jgRfXs073p8B87c/TJamrnIDjbeyYtH5gAe7+TYvsIw";
    byte[] accountKeyBytes = Base64.encodeBase64((this.accountKey + ":" + this.accountKey).getBytes());
    String accountKeyEnc = new String(accountKeyBytes);
    URL url;
    try {
      url = new URL("https://api.datamarket.azure.com/Data.ashx/Bing/Search/v1/Web?Query=%27" + query + "%27&$top="+ top);
      HttpURLConnection conn = (HttpURLConnection)url.openConnection();
      conn.setRequestMethod("GET");
      conn.setRequestProperty("Authorization", "Basic " + accountKeyEnc);

      BufferedReader br = new BufferedReader(new InputStreamReader((conn.getInputStream())));
      String output = "";
      String line;
      while ((line = br.readLine()) != null) {
          output = output + line;
      } 
      //System.out.println(output);
      conn.disconnect();

      DocumentBuilderFactory docBuilderFactory = DocumentBuilderFactory.newInstance();
      DocumentBuilder docBuilder = docBuilderFactory.newDocumentBuilder(); 
      InputSource is = new InputSource(new StringReader(output));
      Document doc = docBuilder.parse(is);
      NodeList urls = doc.getElementsByTagName("d:DisplayUrl");
      int totalUrls = urls.getLength();
      //System.out.println("Number of urls:" +  totalUrls);
      //System.out.println(urls);
      for (int i=0; i<urls.getLength(); i++){
        Element e = (Element)urls.item(i);
        NodeList nl = e.getChildNodes();
        results.add((nl.item(0).getNodeValue()));
      }
	} 
    catch (MalformedURLException e1) {
        e1.printStackTrace();
    } 
    catch (IOException e) {
        e.printStackTrace();
    }
    catch (Exception e){
        e.printStackTrace();
    }
    System.out.println("Number of results: " + String.valueOf(results.size()));
    return results;
  }

  public static void main(String[] args) {
    String queryfile = "conf/queries.txt"; //default
	String outputfile = "results.txt";//default
	if (args.length == 2){
    	outputfile = args[1];
    	queryfile = args[0];
    }

    BingSearch bs = new BingSearch();
    String top = "50"; //default  
	ArrayList<String> results = new ArrayList<String>();
    ArrayList<String> queries = bs.read_queries(queryfile);
	for(String query : queries){
      results.addAll(bs.search(query, top));
    }

    try{
        PrintWriter writer = new PrintWriter(outputfile, "UTF-8");
        for (String result : results){
            writer.println(result);
        }
        writer.close();
    }
    catch(Exception e){
        e.printStackTrace();
    }
  }        
}
