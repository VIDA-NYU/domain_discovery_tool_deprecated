import java.io.*;
import de.l3s.boilerpipe.extractors.ArticleExtractor;
import java.net.URL;
import java.util.*;
import java.util.HashMap;
import java.lang.String;
import java.net.URLDecoder;

public class Extract {
//  static String path;
  private HashMap<String, String> m;

  public Extract()
  {
    m = new HashMap<String, String>();
  }  
  private String readFile(String pathname) throws IOException {
    File file = new File(pathname);
    StringBuilder fileContents = new StringBuilder((int)file.length());
    Scanner scanner = new Scanner(file);
    String lineSeparator = System.getProperty("line.separator");
    try {
        while(scanner.hasNextLine()) {        
            fileContents.append(scanner.nextLine() + lineSeparator);
        }
        return fileContents.toString();
    } finally {
        scanner.close();
    }
  }

  public  void  process(File f, String url)
  {
    try{
/*
      File outputfile = new File(path + "/" + f.getName());
      
      if (!outputfile.exists()){
        PrintWriter writer = new PrintWriter(outputfile.getPath(), "UTF-8");
        String content = readFile(f.getPath());
        writer.print(ArticleExtractor.INSTANCE.getText(content));;
        writer.close();
*/
        
        String content = readFile(f.getPath());
        content = ArticleExtractor.INSTANCE.getText(content);
        content = content.trim().replaceAll(" +", " ");
        content = content.replaceAll("[\n\"\t]", " ");
	content = content.replaceAll(",","");
        System.out.println(url + "\t"  + content);
        
    }
    catch(Exception e){
      System.out.println("process Exception");
    }
     
  }
  public void listFiles(final File folder) {
    for (final File fileEntry : folder.listFiles()) {
        if (fileEntry.isDirectory()) {
            listFiles(fileEntry);
        } else {
            //System.out.println);
            process(fileEntry, URLDecoder.decode(fileEntry.getName()));
        }
    }
  }

  public void getTimestamp(String filename)
  {
    try
    {
      BufferedReader br = new BufferedReader(new FileReader(filename));
      String line;
      while ((line = br.readLine()) != null) 
      {
        try
        {
          String[] url_tp = line.replace("\n", "").split("\t");
          m.put(url_tp[0], url_tp[1]);
        }
        catch(Exception ex)
        {
          ex.printStackTrace();
        }
      }
      br.close();
    }
    catch(Exception ex)
    {
      ex.printStackTrace();
    }
  }  

  public static void main(String[] args) {
    try{
          String inputpath = args[0];
//          String timestampfile = args[1];
          File folder = new File(inputpath);
          Extract e = new Extract();
//          e.getTimestamp(timestampfile);
          e.listFiles(folder);
    } catch(Exception e){
      System.out.println("Exception");
    }
  }
}
