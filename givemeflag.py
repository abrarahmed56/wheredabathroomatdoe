import java.io.PrintStream; 
import java.lang.reflect.Array;   
public class givemeflag {   
    public givemeflag() { 
    }   

    public static void main(String args[]) { 
	if(args.length != 1) { 
	    System.out.println("You are not worthy of receiving the flag."); 
	} 
	else { 
	    String input = args[0];
	    int ai1[] = { 4329, 4347, 4301, 4339, 4351, 4301, 4344, 4339, 4324, 4339, 4301, 4351, 4339, 4321, 4326, 4343, 4320, 4335 }; 
	    int ai[] = new int[input.length()]; 
	    for(int i = 0; i < ai1.length; i++) { 
		ai[i] = input.charAt(i);            //18
		//ai = list(input)
		System.out.println(""+(ai1[i] ^ 0x1092));
		/*if((ai[i] ^ 0x1092) != ai1[i] || input.length() != array.getLength(ai1)) {
		    system.out.println("You are wrong."); system.exit(0); 
		}*/ 
	    }   
	    System.out.println((new StringBuilder()).append("Flag: ").append(input).toString()); 
	} 
    } 
}
