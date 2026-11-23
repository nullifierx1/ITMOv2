#pragma once

#include <core/track.h>

#include <vector>
#include <memory>
#include <string>

namespace mlm {

class Playlist {
public:
	std::vector<std::weak_ptr<Track>>& data() {
		return data_;
	}

	const std::string& name() const {
		return name_; 
	}
	
private:
	std::string name_;
	std::vector<std::weak_ptr<Track>> data_;
};

} // namespace mlm