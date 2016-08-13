public class Test {
  public static void main(String[] args) {
    boolean test = true;
    while (test) {
      System.out.println("Hello World");
      try { Thread.sleep(1000); } catch (Exception e) {}
    }
    System.out.println("Bye-bye");
  }
}
