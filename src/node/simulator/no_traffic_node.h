/*
 * Copyright [2019] [Ke Sun]
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#pragma once

#include <node/simulator/simulator_node.h>

namespace node {

class NoTrafficNode : public SimulatorNode {

private:

  using Base = SimulatorNode;
  using This = NoTrafficNode;

public:

  using Ptr = boost::shared_ptr<This>;
  using ConstPtr = boost::shared_ptr<const This>;

protected:


public:

  NoTrafficNode(ros::NodeHandle nh) : Base(nh) {}

  virtual bool initialize() override;

protected:

  virtual void spawnVehicles() override;

  /// Since there is no agent vehicles in this object, we don't have
  /// to send the goals for the agent vehicles.
  virtual void tickWorld() override {
    world_->Tick();
    updateSimTime();
    publishTraffic();
    sendEgoGoal();
    return;
  }

}; // End class NoTrafficNode.

using NoTrafficNodePtr = NoTrafficNode::Ptr;
using NoTrafficNodeConstPtr = NoTrafficNode::ConstPtr;

} // End namespace node.

