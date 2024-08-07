import 'package:flutter/material.dart';

class HomeScreen extends StatefulWidget {
  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  List<Color> _colors = [Colors.red];

  void _addRectangle() {
    setState(() {
      _colors.add(_colors.length % 2 == 0 ? Colors.green : Colors.blue);
    });
  }

  void _removeLastRectangle() {
    setState(() {
      if (_colors.isNotEmpty) {
        _colors.removeLast();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Home - Cameras'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Expanded(
              child: ListView.builder(
                itemCount: _colors.length,
                itemBuilder: (context, index) {
                  return Container(
                    margin: const EdgeInsets.symmetric(vertical: 8.0),
                    decoration: BoxDecoration(
                      color: _colors[index],
                      borderRadius: BorderRadius.circular(16),
                    ),
                    height: 100,
                  );
                },
              ),
            ),
            SizedBox(height: 16.0),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton(
                  onPressed: _addRectangle,
                  child: Text('Add Rectangle'),
                ),
                ElevatedButton(
                  onPressed: _removeLastRectangle,
                  child: Text('Remove Last Rectangle'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
