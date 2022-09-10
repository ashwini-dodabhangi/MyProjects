import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;

import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		setContentView(R.layout.activity_main);

		
		EditText input, output;
		Button submit, reset;

		input = (EditText) findViewById(R.id.editText);
		output = (EditText) findViewById(R.id.output);

		submit = (Button) findViewById(R.id.submit);

		
		submit.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View v) {

				// Creating a string method argument
				String string = input.getText().toString();

				// Here, we are parsing a string method
				// argument into an integer object
				int i = Integer.parseInt(string, 2);

				// Converts and stores it in the form of string
				String decimal = Integer.toString(i);

				// It will show the output in the second edit text that we created
				output.setText(decimal);
			}
		});

		
		reset = (Button) findViewById(R.id.reset);
		reset.setOnClickListener(new View.OnClickListener() {
			@Override
			public void onClick(View v) {
				input.setText("");
				output.setText("");
			}
		});

	}
}
