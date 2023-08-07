import com.sun.jna.Library;
import com.sun.jna.Native;
import com.sun.jna.Platform;
import com.sun.jna.Pointer;
import com.sun.jna.ptr.PointerByReference;
import com.sun.jna.WString;

import java.io.InputStreamReader;
import java.util.Locale;
import java.util.Scanner;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonElement;
import com.google.gson.JsonParser;

/*콘솔 명령
java파일 작성하고 컴파일
	윈도우
		javac -classpath jna.jar;gson-2.8.4.jar; UTaggerJNA.java -encoding UTF-8  

	centos, linux에서는 classpath 지정하는 방법이 다름
		export CLASSPATH=jna.jar:gson-2.8.4.jar:
		javac UTaggerJNA.java -encoding UTF-8  

실행
	윈도우
		java -classpath jna.jar;gson-2.8.4.jar; UTaggerJNA

	centos, linux에서는 이미 클래스패스를 export로 잡았을테니 
		java UTaggerJNA
*/

interface CLibrary extends Library {
	//public WString get_hello2(WString str);
	WString Global_init2(String file, int option);
	void Global_release();
	WString newUCMA2(int th_num);
	void deleteUCMA(int th_num);
	WString cma_tag_line_BSP(int th_num, WString line, int option);
	//WString cma_tag_sent_depen(int th_num, WString surf, WString tagged);
	WString cma_tag_target_word_json2(int th_num, WString line, int country, int style);
	WString cma_tag_line_json2(int th_num, WString line, int option);
	WString cma_bsp_dep2_js(int th_num, WString surf);
	WString cma_erc(int th_num, WString surf);
	WString cma_ner_js(int th_num, WString surf);
	void cmaReloadCustom(int th_num, byte[] bug);
}

public class UTaggerJNA {

	public static void main(String[] args) {

		System.out.println("자바 유태거 테스트 0.21");

		Scanner scanIn;
		try{
			//아래 UTF-8 지정 부분은 vscode에서 콘솔입력인코딩 문제로 작성한 것이지만 실제론 도움이 안됨.
			//scanIn = new Scanner(new InputStreamReader(System.in, "UTF-8"));
			scanIn = new Scanner(System.in);

			//Locale loc = new Locale("es", "ES");
			//scanIn.useLocale(loc);
		}catch(Exception ex)
		{
			System.out.print(ex.toString());
			return;
		}

		//String dll_pass = "../bin/UTagger.so"; //linux
		String dll_pass = "../bin/UTaggerR64.dll"; // no clr dll
		System.out.println("dll load 시도 : " + dll_pass);

		final CLibrary ut = (CLibrary)Native.loadLibrary(
			dll_pass, CLibrary.class);
		System.out.println("dll load 완료.");

		String path_hlx = "../Hlxcfg.txt";
		String str_debug = ut.Global_init2(path_hlx, 0).toString();
		if(str_debug.length()>0)
		{
			System.out.println(str_debug);
			System.out.println("프로그램 종료1");
			return;
		}
		str_debug = ut.newUCMA2(0).toString();
		if(str_debug.length()>0)
		{
			System.out.println(str_debug);
			System.out.println("프로그램 종료2");
			return;
		}

		while(true)
		{
			System.out.print("0.exit; 1.json기본; 2.json대역어; 3.의존; 4.띄붙; 5.개체명; 6.사용자말뭉치재학습>"); 
			int menu = 0;
			menu = scanIn.nextInt();
			scanIn.nextLine();//개행문자 처리.
			
			if(menu==0) break;
			
			if(menu>0)
			{
				System.out.print("input line : ");
				String line = scanIn.nextLine();
				String gaja = "가1a"; //콘솔 입력과, 하드코딩 입력을 비교하기 위한 것임.
				if(line.length()<=1)
					break;
				WString line_w = new WString(line);
				
				WString tagged_w;
				if(menu==1)
				{
					tagged_w = ut.cma_tag_line_BSP(0, line_w, 2);//형태소 분석
					String tagged = tagged_w.toString();
					System.out.println(tagged);
					
					tagged_w = ut.cma_tag_line_json2(0, line_w, 0);//대역어 없는 분석 결과 출력.
					tagged = tagged_w.toString();
					String pretty = prettyJson(tagged);
					System.out.println( pretty );
				
					//WString depen_w = ut.cma_tag_sent_depen(0, line_w, tagged_w);//의존관계
				}else if(menu==2)
				{
					tagged_w = ut.cma_tag_target_word_json2(0, line_w, 1, 0);//대역어
					String tagged = tagged_w.toString();
					String pretty = prettyJson(tagged);
					System.out.println( pretty );
				}else if(menu==3)
				{
					tagged_w = ut.cma_bsp_dep2_js(0, line_w);//의존
					String tagged = tagged_w.toString();
					String pretty = prettyJson(tagged);
					System.out.println( pretty );
				}else if(menu==4)
				{
					tagged_w = ut.cma_erc(0, line_w);//띄붙
					String tagged = tagged_w.toString();
					System.out.println( tagged);
				}else if(menu==5)
				{
					tagged_w = ut.cma_ner_js(0, line_w);//개체명
					String tagged = tagged_w.toString();
					String pretty = prettyJson(tagged);
					System.out.println( pretty );
				}else if(menu==6)
				{
					byte[] bug = new byte[1000];
					bug[0]=0;
					ut.cmaReloadCustom(0, bug);
					try{
						//String s = new String(bug, "EUC-KR");
						String s = new String(bug, "cp949");
						s = s.replaceAll( "\0", "");
						//System.out.println( bug[0] );
						System.out.println(s);
					}catch(Exception ex)
					{
						System.out.println("exception!!");
						System.out.println(ex.toString());
					}
					

				}
			}
		}
		
		ut.deleteUCMA(0);
		ut.Global_release();
		scanIn.close();
		
		System.out.println("프로그램 종료");
	}
	
	static String prettyJson(String js)
	{
		Gson gson = new GsonBuilder().setPrettyPrinting().create();
		JsonParser jp = new JsonParser();
		JsonElement je = jp.parse(js);
		return gson.toJson(je);
	}
}
