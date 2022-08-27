import {Component, OnInit} from '@angular/core';

@Component({
  selector: 'app-json-workflow',
  templateUrl: './json-workflow.component.html',
  styleUrls: ['./json-workflow.component.scss']
})
export class JsonWorkflowComponent implements OnInit {

  public activeId: number;

  constructor() {
  }

  ngOnInit(): void {
  }
}
